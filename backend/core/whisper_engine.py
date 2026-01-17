"""
核心功能模块 - Whisper引擎
负责语音识别转写功能
"""
import whisper
import os
from typing import List, Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class WhisperEngine:
    """Whisper转写引擎"""
    
    AVAILABLE_MODELS = ['tiny', 'base', 'small', 'medium', 'large']
    
    def __init__(self, model_size: str = "base"):
        """
        初始化Whisper引擎
        
        Args:
            model_size: 模型大小 (tiny/base/small/medium/large)
        """
        if model_size not in self.AVAILABLE_MODELS:
            logger.warning(f"不支持的模型: {model_size}, 使用默认模型 'base'")
            model_size = "base"
        
        self.model_size = model_size
        self.model = None
        logger.info(f"Whisper引擎已初始化，模型: {model_size}")
    
    def load_model(self):
        """加载Whisper模型"""
        if self.model is None:
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
                self.model = whisper.load_model(self.model_size, download_root=download_root)
                logger.info(f"模型加载成功")
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
    
    def transcribe(self, audio_path: str, language: str = "zh", **kwargs) -> Dict:
        """
        转写单个音频文件
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码 (zh/en等)
            **kwargs: 其他whisper参数
            
        Returns:
            包含text和segments的字典
        """
        try:
            # 确保模型已加载
            if self.model is None:
                self.load_model()
            
            logger.info(f"开始转写音频: {audio_path} (语言: {language})")
            
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"音频文件不存在: {audio_path}")
            
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
                
                result = self.transcribe(chunk_path, language)
                all_text.append(result["text"])
                
                # 调整segments的时间偏移
                for segment in result.get("segments", []):
                    segment["start"] += time_offset
                    segment["end"] += time_offset
                    all_segments.append(segment)
                
                # 更新时间偏移（使用最后一个segment的结束时间）
                if result.get("segments"):
                    time_offset = result["segments"][-1]["end"]
            
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
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """获取可用模型列表"""
        return cls.AVAILABLE_MODELS
    
    def get_model_info(self) -> Dict:
        """获取当前模型信息"""
        return {
            "model_size": self.model_size,
            "loaded": self.model is not None,
            "available_models": self.AVAILABLE_MODELS
        }
