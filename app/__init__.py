"""
Flask应用初始化
"""
from flask import Flask
from app.config import Config


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化配置
    config_class.init_app(app)
    
    # 注册路由
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app
