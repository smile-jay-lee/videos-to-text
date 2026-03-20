# Videos to Text - 视频转文字智能转录系统

基于 OpenAI Whisper 的智能语音识别系统，支持视频/音频转文字、AI文本润色和智能摘要生成。

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 项目简介

本项目是一个功能完善的视频/音频转文字工具，提供：

- 🎬 **视频转文字**：支持本地视频文件和B站视频链接
- 🎵 **音频转文字**：支持多种音频格式
- 🤖 **AI智能处理**：文本润色、自动摘要、标点修复
- 🌐 **现代化Web界面**：基于 React + Tailwind CSS
- 📊 **实时进度**：转写过程实时反馈

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask, Python 3.8+ |
| 语音识别 | OpenAI Whisper |
| AI处理 | OpenAI GPT, DeepSeek, Google Gemini |
| 前端 | React 18, Vite, Tailwind CSS |
| 音视频处理 | FFmpeg, MoviePy, Pydub |

## 目录结构

```
videos-to-text/
├── backend/                    # Flask后端
│   ├── app/                   # 应用模块
│   │   ├── config.py          # 配置管理
│   │   └── routes.py          # 路由定义
│   ├── core/                  # 核心功能
│   │   ├── audio_extractor.py # 音频提取
│   │   ├── whisper_engine.py  # Whisper引擎
│   │   └── ai_processor.py    # AI文本处理
│   ├── services/              # 业务服务
│   │   ├── transcription_service.py
│   │   ├── text_service.py
│   │   ├── bili_service.py    # B站支持
│   │   └── gemini_service.py   # Gemini支持
│   ├── utils/                 # 工具模块
│   │   ├── logger.py
│   │   ├── file_handler.py
│   │   └── validators.py
│   ├── main.py               # 应用入口
│   └── requirements.txt      # Python依赖
├── frontend/                  # React前端
│   ├── src/                  # 源代码
│   │   ├── components/       # React组件
│   │   ├── hooks/            # 自定义Hooks
│   │   └── utils/            # 工具函数
│   ├── static/               # 静态资源
│   └── package.json
├── models/                    # Whisper模型目录
├── outputs/                   # 转写结果输出
├── docs/                      # 文档
├── tests/                     # 测试
└── CLAUDE.md                  # AI助手指南
```

## 功能特性

### 核心功能

| 功能 | 描述 |
|------|------|
| 视频转文字 | 支持 MP4, AVI, MOV, MKV, FLV, WMV |
| 音频转文字 | 支持 MP3, WAV, AAC, M4A, FLAC, OGG |
| B站视频 | 支持BV号/bv链接解析下载 |
| 实时进度 | WebSocket/轮询实时显示处理进度 |
| 多语言 | 支持中文、英文等多种语言识别 |

### Whisper 模型选择

| 模型 | 精度 | 内存需求 | 推荐场景 |
|------|------|----------|----------|
| tiny | ⭐ | ~1GB | 快速预览 |
| base | ⭐⭐ | ~1GB | 推荐默认 |
| small | ⭐⭐⭐ | ~2GB | 日常使用 |
| medium | ⭐⭐⭐⭐ | ~5GB | 高精度需求 |
| large | ⭐⭐⭐⭐⭐ | ~10GB | 最佳精度 |

### AI 智能处理

- **文本润色**：修复识别错误，优化标点和格式
- **智能摘要**：自动提取核心内容要点
- **多服务商**：支持 OpenAI GPT / DeepSeek / Google Gemini

## 快速开始

### 环境要求

- Python 3.8+
- FFmpeg（必需）
- Node.js 16+（前端开发）
- 至少 4GB RAM（推荐 8GB+）

### 1. 安装 FFmpeg

**Windows:**
```bash
choco install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 配置
SECRET_KEY=your-secret-key
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Whisper模型
WHISPER_MODEL=base

# AI服务商（至少配置一个）
OPENAI_API_KEY=sk-xxx...
DEEPSEEK_API_KEY=sk-xxx...
GEMINI_API_KEY=xxx...
DEFAULT_AI_PROVIDER=openai
```

### 3. 安装依赖

**后端:**
```bash
cd backend
pip install -r requirements.txt
```

**前端:**
```bash
cd frontend
npm install
```

### 4. 下载 Whisper 模型（首次运行自动下载）

模型默认保存在 `models/` 目录。

### 5. 启动服务

**方式一：前后端分离（推荐）**

终端1 - 启动后端:
```bash
cd backend
python main.py
# 后端: http://localhost:5000
```

终端2 - 启动前端:
```bash
cd frontend
npm run dev
# 前端: http://localhost:3000
```

**方式二：Flask模板（传统模式）**
```bash
cd backend
python main.py
# 访问: http://localhost:5000
```

## 使用说明

### 本地文件转写

1. 打开前端页面
2. 选择视频或音频文件
3. 选择识别语言
4. 选择 Whisper 模型大小
5. 点击开始转写
6. 等待处理完成，下载 TXT 文件

### B站视频转写

1. 输入 B站视频链接或 BV号
2. 系统自动解析并下载
3. 自动进行转写

### AI 智能处理

1. 转写完成后
2. 点击"润色"按钮优化文本
3. 点击"摘要"生成内容概要
4. 支持一键导出

## API 接口

### 上传文件
```
POST /upload
Content-Type: multipart/form-data

Response:
{
    "success": true,
    "task_id": "uuid",
    "filename": "video.mp4"
}
```

### 开始转写
```
POST /api/transcribe
{
    "task_id": "uuid",
    "language": "zh",
    "model": "base"
}
```

### 查询状态
```
GET /api/task/{task_id}
{
    "success": true,
    "status": "processing",
    "progress": 50,
    "message": "正在转写..."
}
```

### 获取结果
```
GET /api/result/{task_id}
{
    "success": true,
    "text": "转写内容..."
}
```

## 配置说明

### Whisper 配置（防幻觉参数）

推荐配置（见 `whisper_engine.py`）：
```python
'condition_on_previous_text': False,  # 防止误修正
'compression_ratio_threshold': 2.4,   # 压缩比阈值
'logprob_threshold': -1.0,              # 对数概率阈值
'no_speech_threshold': 0.6,             # 无声检测阈值
```

### 文件大小限制

默认 2GB，可在 `config.py` 中修改：
```python
MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024
```

## 常见问题

### Q: 提示 "FFmpeg not found"
确保 FFmpeg 已安装并添加到系统 PATH 环境变量。

### Q: 转写速度慢
- 使用更小的模型（tiny/base）
- 确保足够的系统内存
- 建议使用 GPU 加速

### Q: 内存不足
- 减小 Whisper 模型大小
- 处理较小的文件
- 增加系统内存

### Q: AI 功能不可用
- 检查 `.env` 中的 API 密钥配置
- 确保网络连接正常
- 检查 API 额度是否充足

## 部署

### 使用 Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Docker 部署
```bash
docker build -t video-to-text .
docker run -p 5000:5000 -v $(pwd)/outputs:/app/outputs video-to-text
```

## 安全建议

- 生产环境修改 `SECRET_KEY` 为强随机密钥
- 不要将 `.env` 提交到版本控制
- 生产环境建议使用 HTTPS
- 定期清理 `outputs/` 和 `uploads/` 目录

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别模型
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [React](https://react.dev/) - UI框架
- [Tailwind CSS](https://tailwindcss.com/) - CSS框架
- [MoviePy](https://zulko.github.io/moviepy/) - 视频处理

---

**如果项目对你有帮助，请给个 Star ⭐**
