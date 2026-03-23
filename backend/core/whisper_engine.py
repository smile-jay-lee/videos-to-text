"""
核心功能模块 - Whisper引擎
负责语音识别转写功能
"""
import os
import gc
from typing import List, Dict
from utils.logger import get_logger
logger = get_logger(__name__)

# 注意：whisper 在 load_model() 内延迟导入，避免 numba/numpy 版本冲突影响应用启动


class WhisperEngine:
    """Whisper转写引擎（支持本地/服务器优化模式）"""
    
    AVAILABLE_MODELS = ['tiny', 'base', 'small', 'medium', 'large']
    
    def __init__(
        self,
        model_size: str = "base",
        mode: str = "local"
    ):
        """
        初始化Whisper引擎
        
        Args:
            model_size: 模型大小 (tiny/base/small/medium/large)
            mode: 运行模式 ('local' 或 'server')
        """
        import torch

        if model_size not in self.AVAILABLE_MODELS:
            logger.warning(f"不支持的模型: {model_size}, 使用默认模型 'base'")
            model_size = "base"
        
        self.model_size = model_size
        self.model = None
        
        normalized_mode = (mode or "local").lower()
        if normalized_mode not in ("local", "server"):
            logger.warning(f"不支持的模式: {mode}, 使用默认模式 'local'")
            normalized_mode = "local"

        self.mode = normalized_mode
        
        if self.mode == 'local':
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.fp16 = True if self.device == "cuda" else False
            self.server_config = {
                'enable_chunking': False,
                'unload_after_use': False,
            }
        else:
            self.device = 'cpu'
            self.fp16 = False
            self.server_config = {
                'enable_chunking': True,
                'chunk_size': 45,
                'max_audio_duration': 180,
                'unload_after_use': True,
            }
        
        logger.info(f"Whisper引擎已初始化 [模式: {self.mode}, 模型: {model_size}, 设备: {self.device}]")
        if self.mode == 'server':
            logger.info(f"服务器优化已启用: 分块={self.server_config['enable_chunking']}, "
                       f"块大小={self.server_config['chunk_size']}秒, "
                       f"自动卸载={self.server_config['unload_after_use']}")
    
    def load_model(self):
        """加载Whisper模型"""
        if self.model is None:
            import whisper  # 延迟导入：避免 numba/numpy 版本冲突在应用启动时报错
            logger.info(f"正在加载Whisper模型: {self.model_size}")
            try:
                # 使用项目根目录下的 models 文件夹
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                download_root = os.path.join(base_dir, 'models')
                os.makedirs(download_root, exist_ok=True)
                
                model_file = os.path.join(download_root, f"{self.model_size}.pt")
                
                # 检查文件是否存在但损坏（参考whisper源码的校验逻辑）
                if os.path.exists(model_file):
                    try:
                        # 尝试简单校验：文件能否打开且大小合理
                        file_size = os.path.getsize(model_file)
                        if file_size < 1024 * 1024:  # 小于1MB肯定是损坏的
                            logger.warning(f"检测到损坏的模型文件({file_size} bytes)，删除重新下载")
                            os.remove(model_file)
                    except Exception as check_err:
                        logger.warning(f"检查模型文件时出错: {check_err}")
                
                # 加载模型（如果文件损坏，whisper会自动重新下载）
                self.model = whisper.load_model(
                    self.model_size,
                    download_root=download_root,
                    device=self.device
                )
                logger.info(f"模型加载成功")
                
                # 服务器模式：加载后立即回收内存
                if self.mode == 'server':
                    gc.collect()
                    logger.debug("已执行内存回收（模型加载后）")
                    
            except RuntimeError as e:
                # 捕获SHA256校验失败的错误
                if "SHA256 checksum does not" in str(e):
                    logger.error(f"模型文件校验失败，尝试删除损坏文件: {model_file}")
                    if os.path.exists(model_file):
                        os.remove(model_file)
                    logger.info("请重新运行程序以重新下载模型")
                raise
            except Exception as e:
                logger.error(f"加载模型失败: {str(e)}")
                raise
    
    def transcribe(
        self,
        audio_path: str,
        language: str = "zh",
        auto_unload: bool = True,
        **kwargs
    ) -> Dict:
        """
        转写单个音频文件
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码 (zh/en等)
            auto_unload: 是否在转写结束后自动卸载模型（server模式）
            **kwargs: 其他whisper参数
            
        Returns:
            包含text和segments的字典
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"音频文件不存在: {audio_path}")
            
            # 确保模型已加载
            if self.model is None:
                self.load_model()
            
            logger.info(f"开始转写音频: {audio_path} (语言: {language})")
            
            # 准备转写参数
            transcribe_options = {
                'language': language,
                'verbose': False,
                'task': 'transcribe',  # 明确指定任务为转录（而非翻译）
                # 防幻觉参数（重要！）
                'condition_on_previous_text': False,  # 不基于前文生成，避免重复
                'compression_ratio_threshold': 2.4,   # 检测重复内容
                'logprob_threshold': -1.0,            # 质量阈值
                'no_speech_threshold': 0.6,           # 静音检测阈值
                'fp16': self.fp16,
            }
            
            # 如果是中文，添加优化参数
            if language == 'zh':
                transcribe_options.update({
                    'initial_prompt': '以下是普通话的句子。',  # 提示模型这是中文
                    'temperature': 0.0,  # 降低随机性，提高准确度
                })
            
            # 合并用户自定义参数
            transcribe_options.update(kwargs)
            
            # 执行转写
            result = self.model.transcribe(audio_path, **transcribe_options)
            
            text = result.get("text", "")
            segments = result.get("segments", [])
            
            logger.info(f"转写完成，文本长度: {len(text)} 字符")
            
            return {
                "text": text.strip(),
                "segments": segments,
                "language": result.get("language", language)
            }
            
        except Exception as e:
            logger.error(f"转写失败: {str(e)}")
            raise
        finally:
            if self.mode == 'server':
                gc.collect()
                logger.debug("已执行内存回收（transcribe 结束）")
                if self.server_config.get('unload_after_use') and auto_unload:
                    self._unload_model()
    
    def transcribe_chunks(self, chunk_paths: List[str], language: str = "zh") -> Dict:
        """
        转写多个音频片段并合并结果
        
        Args:
            chunk_paths: 音频片段路径列表
            language: 语言代码
            
        Returns:
            包含合并后text和所有segments的字典
        """
        try:
            if not chunk_paths:
                raise ValueError("音频片段列表为空")
            
            logger.info(f"开始转写 {len(chunk_paths)} 个音频片段")
            
            all_text = []
            all_segments = []
            time_offset = 0.0
            
            for i, chunk_path in enumerate(chunk_paths):
                logger.info(f"正在转写第 {i+1}/{len(chunk_paths)} 段")
                
                try:
                    result = self.transcribe(chunk_path, language, auto_unload=False)
                    all_text.append(result["text"])
                    
                    # 调整segments的时间偏移
                    for segment in result.get("segments", []):
                        segment["start"] += time_offset
                        segment["end"] += time_offset
                        all_segments.append(segment)
                    
                    # 更新时间偏移（使用最后一个segment的结束时间）
                    if result.get("segments"):
                        time_offset = result["segments"][-1]["end"]
                    
                    # 服务器模式：每处理完一个块后回收内存
                    if self.mode == 'server':
                        gc.collect()
                        logger.debug(f"已执行内存回收（第 {i+1} 块处理后）")
                finally:
                    if os.path.exists(chunk_path):
                        try:
                            os.remove(chunk_path)
                            logger.debug(f"已清理临时片段: {chunk_path}")
                        except OSError as remove_err:
                            logger.warning(f"清理临时片段失败: {chunk_path}, 错误: {remove_err}")
            
            # 合并文本
            full_text = " ".join(all_text)
            
            logger.info(f"所有片段转写完成，总文本长度: {len(full_text)} 字符")
            
            return {
                "text": full_text.strip(),
                "segments": all_segments,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"分段转写失败: {str(e)}")
            raise
        finally:
            if self.mode == 'server':
                gc.collect()
                if self.server_config.get('unload_after_use'):
                    self._unload_model()
    
    def _unload_model(self):
        """卸载模型以释放内存（仅服务器模式）"""
        if self.model is not None:
            logger.info("正在卸载模型以释放内存...")
            del self.model
            self.model = None
            gc.collect()
            logger.info("模型已卸载，内存已释放")
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """获取可用模型列表"""
        return cls.AVAILABLE_MODELS
    
    def get_model_info(self) -> Dict:
        """获取当前模型信息"""
        return {
            "model_size": self.model_size,
            "loaded": self.model is not None,
            "available_models": self.AVAILABLE_MODELS,
            "mode": self.mode,
            "device": self.device,
            "server_config": self.server_config if self.mode == 'server' else None
        }
    
    def get_config_summary(self) -> str:
        """获取配置摘要（用于日志输出）"""
        summary = f"Whisper配置 - 模式: {self.mode}, 模型: {self.model_size}, 设备: {self.device}"
        if self.mode == 'server':
            summary += f"\n  服务器优化: 分块处理={self.server_config['enable_chunking']}"
            summary += f", 块大小={self.server_config['chunk_size']}秒"
            summary += f", 最大时长={self.server_config['max_audio_duration']}秒"
            summary += f", 自动卸载={self.server_config['unload_after_use']}"
        return summary
