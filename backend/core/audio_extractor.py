"""
核心功能模块 - 音频提取器
负责从视频中提取音频，转换格式，分割大文件
"""
import os
import json
import glob
import subprocess
from typing import List
from utils.logger import get_logger

logger = get_logger(__name__)


class AudioExtractor:
    """音频提取和处理核心类"""
    
    def __init__(self, mode: str = "local"):
        self.temp_files = []
        normalized_mode = (mode or "local").lower()
        self.mode = normalized_mode if normalized_mode in ("local", "server") else "local"

    def _threads_param(self) -> List[str]:
        return ['-threads', '1'] if self.mode == 'server' else []

    def _run_ffmpeg(self, args: List[str], error_message: str):
        command = ['ffmpeg', '-y', *args]
        try:
            result = subprocess.run(
                command, 
                check=True, 
                capture_output=True, 
                encoding='utf-8',
                errors='ignore'
            )
        except subprocess.CalledProcessError as e:
            stderr = e.stderr if isinstance(e.stderr, str) else (
                e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
            )
            logger.error(f"{error_message}: {stderr}")
            raise
    
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
            self._run_ffmpeg([
                '-i', video_path,
                '-vn',
                '-acodec', 'libmp3lame',
                '-q:a', '2',
                *self._threads_param(),
                output_path
            ], "提取音频失败")
            
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
            self._run_ffmpeg([
                '-i', input_path,
                *self._threads_param(),
                output_path
            ], "转换音频格式失败")
            
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
            base_name = os.path.splitext(audio_path)[0]
            chunk_seconds = max(1, int(chunk_duration_ms / 1000))
            output_pattern = f"{base_name}_chunk_%03d.mp3"

            # 检查文件扩展名，m4a/aac需要重新编码
            file_ext = os.path.splitext(audio_path)[1].lower()
            if file_ext in ['.m4a', '.aac']:
                # 需要重新编码为mp3
                self._run_ffmpeg([
                    '-i', audio_path,
                    '-f', 'segment',
                    '-segment_time', str(chunk_seconds),
                    '-acodec', 'libmp3lame',
                    '-q:a', '2',
                    *self._threads_param(),
                    output_pattern
                ], "分割音频失败")
            else:
                # 其他格式尝试直接复制
                self._run_ffmpeg([
                    '-i', audio_path,
                    '-f', 'segment',
                    '-segment_time', str(chunk_seconds),
                    '-c', 'copy',
                    *self._threads_param(),
                    output_pattern
                ], "分割音频失败")

            chunk_glob = f"{base_name}_chunk_*.mp3"
            chunks = sorted(glob.glob(chunk_glob))
            self.temp_files.extend(chunks)

            logger.info(f"音频分割完成，共 {len(chunks)} 段")
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
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration,size,format_name',
                '-of', 'json',
                audio_path,
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            metadata = json.loads(result.stdout or '{}')
            format_info = metadata.get('format', {})
            file_size = os.path.getsize(audio_path)
            duration_seconds = float(format_info.get('duration', 0.0) or 0.0)
            
            info = {
                'duration_seconds': duration_seconds,
                'duration_formatted': self._format_duration(duration_seconds),
                'file_size_mb': file_size / (1024 * 1024),
                'format': format_info.get('format_name', os.path.splitext(audio_path)[1][1:]),
                'metadata': metadata
            }
            
            logger.info(f"音频信息: {info}")
            return info
            
        except subprocess.CalledProcessError as e:
            logger.error(f"获取音频信息失败: {e.stderr or str(e)}")
            raise
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
