"""
Flask应用初始化
"""
import os
from flask import Flask
from flask_cors import CORS
from app.config import Config


def create_app(config_class=Config):
    """应用工厂函数"""
    # 设置template和static文件夹路径
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend-old', 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend-old', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(config_class)
    
    # 启用CORS
    CORS(app)
    
    # 初始化配置
    config_class.init_app(app)
    
    # 注册API路由（用于React前端）
    from app.api_routes import api_bp
    app.register_blueprint(api_bp)
    
    # 注册传统路由（用于模板渲染，可选）
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app
