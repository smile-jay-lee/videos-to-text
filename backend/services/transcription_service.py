"""
业务逻辑层 - 转写服务
"""
import os
import uuid
from typing import Dict, Optional
from core import AudioExtractor, WhisperEngine
from utils.logger import get_logger
from utils.file_handler import get_file_size_mb
from utils.validators import is_video_file, is_audio_file

logger = get_logger(__name__)


class TranscriptionService:
    """转写服务"""
    
    # 大文件阈值（MB）
    LARGE_FILE_THRESHOLD = 25
    
    def __init__(self, model_size: str = "base"):
        """
        初始化转写服务
        
        Args:
            model_size: Whisper模型大小
        """
        self.engine = WhisperEngine(model_size)
        self.audio_extractor = AudioExtractor()
        logger.info(f"转写服务已初始化，模型: {model_size}")
    
    def transcribe_file(
        self,
        file_path: str,
        language: str = "zh",
        task_id: str = None,
        progress_callback = None
    ) -> Dict:
        """
        转写文件（视频或音频）
        
        Args:
            file_path: 文件路径
            language: 语言代码
            task_id: 任务ID
            progress_callback: 进度回调函数
            
        Returns:
            包含text和segments的字典
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            task_id = task_id or str(uuid.uuid4())
            logger.info(f"开始转写任务: {task_id}, 文件: {file_path}")
            
            # 报告进度：开始处理
            if progress_callback:
                progress_callback(task_id, 10, "正在处理文件...")
            
            # 判断文件类型并处理
            audio_path = self._prepare_audio(file_path, task_id, progress_callback)
            
            # 报告进度：准备转写
            if progress_callback:
                progress_callback(task_id, 30, "音频已准备，开始转写...")
            
            # 检查文件大小，决定是否分段
            file_size_mb = get_file_size_mb(audio_path)
            
            if file_size_mb > self.LARGE_FILE_THRESHOLD:
                logger.info(f"文件较大 ({file_size_mb:.2f}MB)，将进行分段处理")
                result = self._transcribe_large_file(
                    audio_path, language, task_id, progress_callback
                )
            else:
                result = self._transcribe_single_file(
                    audio_path, language, task_id, progress_callback
                )
            
            # 报告进度：完成
            if progress_callback:
                progress_callback(task_id, 100, "转写完成")
            
            logger.info(f"转写任务完成: {task_id}")
            return result
            
        except Exception as e:
            logger.error(f"转写任务失败 {task_id}: {str(e)}")
            if progress_callback:
                progress_callback(task_id, -1, f"转写失败: {str(e)}")
            raise
        finally:
            # 清理临时文件
            self.audio_extractor.cleanup_temp_files()
    
    def _prepare_audio(
        self,
        file_path: str,
        task_id: str,
        progress_callback = None
    ) -> str:
        """准备音频文件"""
        if is_video_file(file_path):
            logger.info("检测到视频文件，提取音频...")
            if progress_callback:
                progress_callback(task_id, 15, "正在从视频提取音频...")
            
            audio_path = self.audio_extractor.extract_from_video(file_path)
            return audio_path
        
        elif is_audio_file(file_path):
            logger.info("检测到音频文件，直接使用")
            return file_path
        
        else:
            raise ValueError("不支持的文件类型")
    
    def _transcribe_single_file(
        self,
        audio_path: str,
        language: str,
        task_id: str,
        progress_callback = None
    ) -> Dict:
        """转写单个文件"""
        if progress_callback:
            progress_callback(task_id, 50, "正在转写音频...")
        
        # 加载模型
        self.engine.load_model()
        
        # 转写
        result = self.engine.transcribe(audio_path, language)
        
        if progress_callback:
            progress_callback(task_id, 90, "转写完成，正在整理结果...")
        
        return result
    
    def _transcribe_large_file(
        self,
        audio_path: str,
        language: str,
        task_id: str,
        progress_callback = None
    ) -> Dict:
        """转写大文件（分段处理）"""
        # 分割音频
        if progress_callback:
            progress_callback(task_id, 35, "正在分割音频...")
        
        chunks = self.audio_extractor.split_audio(audio_path)
        logger.info(f"音频已分割为 {len(chunks)} 段")
        
        # 加载模型
        self.engine.load_model()
        
        # 分段转写
        chunk_progress_start = 40
        chunk_progress_range = 50
        
        for i, chunk_path in enumerate(chunks):
            progress = chunk_progress_start + (i + 1) / len(chunks) * chunk_progress_range
            if progress_callback:
                progress_callback(
                    task_id,
                    int(progress),
                    f"正在转写第 {i+1}/{len(chunks)} 段..."
                )
        
        result = self.engine.transcribe_chunks(chunks, language)
        
        return result
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        return self.engine.get_model_info()
