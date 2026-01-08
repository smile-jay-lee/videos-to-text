"""
工具模块 - 文件处理
"""
import os
import hashlib
import shutil
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def ensure_dir(directory: str):
    """确保目录存在，不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"创建目录: {directory}")


def get_file_md5(file_path: str) -> str:
    """计算文件MD5值"""
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def get_file_size_mb(file_path: str) -> float:
    """获取文件大小（MB）"""
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


def cleanup_file(file_path: str):
    """安全删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"已删除文件: {file_path}")
    except Exception as e:
        logger.warning(f"删除文件失败 {file_path}: {str(e)}")


def cleanup_directory(directory: str):
    """删除目录及其内容"""
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            logger.info(f"已删除目录: {directory}")
    except Exception as e:
        logger.warning(f"删除目录失败 {directory}: {str(e)}")


def get_safe_filename(filename: str) -> str:
    """获取安全的文件名（移除特殊字符）"""
    import re
    # 移除或替换不安全的字符
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return safe_name


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
