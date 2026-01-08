"""
工具模块 - 验证器
"""
import os
from typing import Tuple
from werkzeug.utils import secure_filename

# 允许的文件扩展名
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'aac', 'm4a', 'flac', 'ogg'}
ALLOWED_EXTENSIONS = ALLOWED_VIDEO_EXTENSIONS | ALLOWED_AUDIO_EXTENSIONS

# 最大文件大小 (500MB)
MAX_FILE_SIZE = 500 * 1024 * 1024


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_video_file(filename: str) -> bool:
    """检查是否为视频文件"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


def is_audio_file(filename: str) -> bool:
    """检查是否为音频文件"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS


def validate_file(file, max_size: int = MAX_FILE_SIZE) -> Tuple[bool, str]:
    """
    验证上传的文件
    
    Args:
        file: 上传的文件对象
        max_size: 最大文件大小（字节）
        
    Returns:
        (是否有效, 错误信息)
    """
    # 检查文件是否存在
    if not file:
        return False, "未选择文件"
    
    # 检查文件名
    if file.filename == '':
        return False, "文件名为空"
    
    # 检查文件扩展名
    if not allowed_file(file.filename):
        return False, f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # 检查文件大小（如果可能）
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f"文件过大，最大支持 {max_size_mb:.0f}MB"
    
    if file_size == 0:
        return False, "文件为空"
    
    return True, ""


def get_secure_filename(filename: str) -> str:
    """获取安全的文件名"""
    return secure_filename(filename)


def validate_language_code(lang_code: str) -> bool:
    """验证语言代码"""
    supported_languages = ['zh', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'ru']
    return lang_code in supported_languages
