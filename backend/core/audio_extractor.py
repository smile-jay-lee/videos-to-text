"""
核心功能模块 - 音频提取器
负责从视频中提取音频，转换格式，分割大文件
"""
import os
import math
try:
    from moviepy import VideoFileClip
except ImportError:
    from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from typing import List, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)


class AudioExtractor:
    """音频提取和处理核心类"""
    
    def __init__(self):
        self.temp_files = []
    
    def extract_from_video(self, video_path: str, output_path: str = None) -> str:
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            output_path: 输出音频路径，如果为None则自动生成
            
        Returns:
            音频文件路径
        """
        try:
            if output_path is None:
                base_name = os.path.splitext(video_path)[0]
                output_path = f"{base_name}_audio.mp3"
            
            logger.info(f"正在从视频提取音频: {video_path}")
            video = VideoFileClip(video_path)
            audio = video.audio
            
            if audio is None:
                raise ValueError("视频中没有音频轨道")
            
            audio.write_audiofile(output_path, logger=None)
            video.close()
            
            logger.info(f"音频已提取: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"提取音频失败: {str(e)}")
            raise
    
    def convert_format(self, input_path: str, output_format: str = "mp3") -> str:
        """
        转换音频格式
        
        Args:
            input_path: 输入音频路径
            output_format: 目标格式（mp3, wav等）
            
        Returns:
            转换后的文件路径
        """
        try:
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}.{output_format}"
            
            logger.info(f"正在转换音频格式: {input_path} -> {output_format}")
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format=output_format)
            
            logger.info(f"格式转换完成: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"转换音频格式失败: {str(e)}")
            raise
    
    def split_audio(self, audio_path: str, chunk_duration_ms: int = 10*60*1000) -> List[str]:
        """
        分割大音频文件
        
        Args:
            audio_path: 音频文件路径
            chunk_duration_ms: 每段时长（毫秒），默认10分钟
            
        Returns:
            音频片段路径列表
        """
        try:
            logger.info(f"正在分割音频: {audio_path}")
            audio = AudioSegment.from_file(audio_path)
            chunks = []
            
            num_chunks = math.ceil(len(audio) / chunk_duration_ms)
            logger.info(f"将分割为 {num_chunks} 段")
            
            base_name = os.path.splitext(audio_path)[0]
            
            for i in range(num_chunks):
                start_ms = i * chunk_duration_ms
                end_ms = min((i+1) * chunk_duration_ms, len(audio))
                chunk = audio[start_ms:end_ms]
                
                chunk_path = f"{base_name}_chunk_{i}.mp3"
                # 导出时明确指定参数，确保音轨正确保存
                chunk.export(
                    chunk_path,
                    format="mp3",
                    bitrate="192k",  # 指定比特率
                    parameters=["-ac", "2"]  # 确保双声道（或保持原声道）
                )
                chunks.append(chunk_path)
                self.temp_files.append(chunk_path)
                
                logger.info(f"已创建音频片段 {i+1}/{num_chunks}: {chunk_path} ({len(chunk)/1000:.1f}s)")
            
            return chunks
            
        except Exception as e:
            logger.error(f"分割音频失败: {str(e)}")
            raise
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        获取音频信息
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            包含时长、格式、大小等信息的字典
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            file_size = os.path.getsize(audio_path)
            
            info = {
                'duration_seconds': len(audio) / 1000,
                'duration_formatted': self._format_duration(len(audio) / 1000),
                'channels': audio.channels,
                'sample_rate': audio.frame_rate,
                'file_size_mb': file_size / (1024 * 1024),
                'format': os.path.splitext(audio_path)[1][1:]
            }
            
            logger.info(f"音频信息: {info}")
            return info
            
        except Exception as e:
            logger.error(f"获取音频信息失败: {str(e)}")
            raise
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"已删除临时文件: {file_path}")
            except Exception as e:
                logger.warning(f"删除临时文件失败 {file_path}: {str(e)}")
        
        self.temp_files.clear()
    
    @staticmethod
    def _format_duration(seconds: float) -> str:
        """格式化时长为 HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
