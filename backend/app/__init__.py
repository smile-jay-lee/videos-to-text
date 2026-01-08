"""
Flask应用初始化
"""
import os
from flask import Flask
from app.config import Config


def create_app(config_class=Config):
    """应用工厂函数"""
    # 设置template和static文件夹路径
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend', 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(config_class)
    
    # 初始化配置
    config_class.init_app(app)
    
    # 注册路由
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app
