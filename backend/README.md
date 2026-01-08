# Backend - 视频转文字后端

## 目录结构

```
backend/
├── app/              # Flask应用
│   ├── __init__.py   # 应用工厂
│   ├── config.py     # 配置文件
│   └── routes.py     # 路由处理
├── core/             # 核心功能模块
│   ├── audio_extractor.py    # 音频提取
│   ├── whisper_engine.py     # Whisper转录引擎
│   └── ai_processor.py       # AI处理
├── services/         # 业务逻辑层
│   ├── transcription_service.py  # 转录服务
│   └── text_service.py           # 文本处理服务
├── utils/            # 工具类
│   ├── file_handler.py   # 文件处理
│   ├── logger.py         # 日志工具
│   └── validators.py     # 验证器
├── main.py           # 应用入口
└── requirements.txt  # Python依赖
```

## 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 配置环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
# OpenAI API配置
OPENAI_API_KEY=your_api_key_here

# Whisper模型
WHISPER_MODEL=base

# 应用配置
DEBUG=true
HOST=0.0.0.0
PORT=5000
```

## 运行

```bash
python main.py
```

服务将运行在 http://localhost:5000
