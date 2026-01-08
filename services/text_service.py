"""
业务逻辑层 - 文本服务
"""
import os
from typing import Dict, Optional
from core import AIProcessor
from utils.logger import get_logger

logger = get_logger(__name__)


class TextService:
    """文本处理服务"""
    
    def __init__(self, ai_provider: Optional[str] = None, api_key: Optional[str] = None):
        """
        初始化文本服务
        
        Args:
            ai_provider: AI提供商 (openai/deepseek)
            api_key: API密钥
        """
        self.processor = None
        
        if ai_provider:
            try:
                self.processor = AIProcessor(ai_provider, api_key)
                logger.info(f"文本服务已初始化，AI提供商: {ai_provider}")
            except Exception as e:
                logger.warning(f"初始化AI处理器失败: {str(e)}")
    
    def process_text(
        self,
        text: str,
        refine: bool = True,
        summarize: bool = True
    ) -> Dict:
        """
        处理文本（润色和/或总结）
        
        Args:
            text: 原始文本
            refine: 是否润色
            summarize: 是否生成摘要
            
        Returns:
            包含处理结果的字典
        """
        if not self.processor:
            logger.warning("AI处理器未初始化，返回原文")
            return {
                "original": text,
                "refined": None,
                "summary": None,
                "error": "AI处理器未配置"
            }
        
        try:
            result = self.processor.process_text(text, refine, summarize)
            logger.info("文本处理完成")
            return result
            
        except Exception as e:
            logger.error(f"文本处理失败: {str(e)}")
            return {
                "original": text,
                "refined": None,
                "summary": None,
                "error": str(e)
            }
    
    def export_to_txt(self, text: str, output_path: str) -> str:
        """
        导出为TXT文件
        
        Args:
            text: 文本内容
            output_path: 输出路径
            
        Returns:
            文件路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            logger.info(f"已导出TXT文件: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"导出TXT失败: {str(e)}")
            raise
    
    def export_to_srt(self, segments: list, output_path: str) -> str:
        """
        导出为SRT字幕文件
        
        Args:
            segments: Whisper返回的segments列表
            output_path: 输出路径
            
        Returns:
            文件路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments, 1):
                    # SRT格式
                    # 序号
                    f.write(f"{i}\n")
                    # 时间戳
                    start = self._format_timestamp(segment['start'])
                    end = self._format_timestamp(segment['end'])
                    f.write(f"{start} --> {end}\n")
                    # 文本
                    f.write(f"{segment['text'].strip()}\n\n")
            
            logger.info(f"已导出SRT文件: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"导出SRT失败: {str(e)}")
            raise
    
    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """格式化时间戳为SRT格式 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
