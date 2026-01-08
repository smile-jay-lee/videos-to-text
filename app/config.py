"""
Flask应用配置
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    OUTPUT_FOLDER = 'outputs'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    
    # Whisper配置
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
    DEFAULT_LANGUAGE = 'zh'
    
    # AI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEFAULT_AI_PROVIDER = os.getenv('DEFAULT_AI_PROVIDER', 'openai')
    
    # 应用配置
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    @staticmethod
    def init_app(app):
        """初始化应用"""
        # 确保必要的目录存在
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
