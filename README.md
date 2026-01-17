# Videos to Text - 视频转文字智能转录系统

基于 OpenAI Whisper 的智能语音识别系统，支持视频/音频转文字、AI文本润色和智能摘要生成。

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ 主要功能

- 🎬 **视频/音频转文字**：支持MP4、AVI、MOV、MP3、WAV等多种格式
- 🤖 **AI智能润色**：自动修正识别错误，优化文本格式
- 📝 **智能摘要生成**：快速提取核心内容要点
- 📊 **多格式导出**：支持TXT、SRT字幕格式
- 📜 **历史记录管理**：查看、管理和删除过往的转录任务
- 🌐 **Web界面**：基于 React 的现代化交互界面
- ⚡ **大文件支持**：支持超大文件处理（最大2GB）

## 📁 项目结构

```
videos-to-text/
├── backend/              # 后端代码
│   ├── app/              # Flask应用
│   ├── core/             # 核心功能（音频提取、Whisper引擎、AI处理）
│   ├── services/         # 业务逻辑层
│   ├── utils/            # 工具类
│   ├── main.py           # 应用入口
│   └── requirements.txt  # Python依赖
├── frontend/             # 前端代码 (React + Vite)
│   ├── src/              # 源代码
│   └── package.json      # 项目配置
├── history/              # 历史文件和早期版本
├── outputs/              # 输出文件目录
├── .env                  # 环境变量配置（不提交到Git）
├── .env.example          # 环境变量示例
└── README.md             # 项目说明

## 🖼️ 功能展示

### 支持的格式

**视频格式**：MP4, AVI, MOV, MKV, FLV, WMV  
**音频格式**：MP3, WAV, AAC, M4A, FLAC, OGG

### Whisper模型

- `tiny` - 最快（~1GB内存）
- `base` - 推荐（~1GB内存）
- `small` - 较准确（~2GB内存）
- `medium` - 很准确（~5GB内存）
- `large` - 最准确（~10GB内存）

## 📦 安装说明

### 1. 系统要求

- Python 3.8 或更高版本
- FFmpeg（必需）
- 至少 4GB RAM（推荐 8GB+）

### 2. 安装 FFmpeg

**Windows:**
```bash
# 使用 Chocolatey
choco install ffmpeg

# 或下载并添加到PATH
# https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. 克隆项目

```bash
git clone https://github.com/smile-jay-lee/videos-to-text.git
cd videos-to-text
```

### 4. 安装Python依赖

```bash
cd backend
pip install -r requirements.txt
```

### 5. 配置环境变量

在项目根目录复制 `.env.example` 为 `.env` 并配置：

```bash
# Flask配置
SECRET_KEY=your-secret-key-here
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Whisper配置
WHISPER_MODEL=base

# AI配置（可选）
OPENAI_API_KEY=your-openai-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
DEFAULT_AI_PROVIDER=openai
```

## 🚀 使用方法

### 方式一：React 前端 + API 后端（推荐）

**1. 启动后端API服务:**
```bash
cd backend
python main.py
```
后端运行在 http://localhost:5000

**2. 启动React前端:**
```bash
cd frontend
npm install  # 首次运行需要安装依赖
npm run dev
```
前端运行在 http://localhost:3000

### 方式二：传统Flask模板（备选）

```bash
cd backend
python main.py
```
直接访问 http://localhost:5000

访问 `http://localhost:5000` 即可使用。

### 使用步骤

1. **上传文件**：选择视频或音频文件
2. **选择设置**：选择语言和模型大小
3. **开始转写**：点击上传按钮，等待处理完成
4. **查看结果**：转写完成后自动跳转到结果页面
5. **下载文件**：可下载TXT或SRT格式

## 📁 项目结构

```
video-to-text/
├── app/                      # Flask应用
│   ├── __init__.py           # 应用工厂
│   ├── config.py             # 配置管理
│   ├── routes.py             # 路由定义
│   ├── templates/            # HTML模板
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── upload.html
│   │   └── result.html
│   └── static/               # 静态文件
│       ├── css/
│       │   └── style.css
│       ├── js/
│       └── uploads/          # 上传文件临时存储
│
├── core/                     # 核心功能
│   ├── audio_extractor.py    # 音频提取器
│   ├── whisper_engine.py     # Whisper引擎
│   └── ai_processor.py       # AI文本处理器
│
├── services/                 # 业务逻辑
│   ├── transcription_service.py  # 转写服务
│   └── text_service.py       # 文本服务
│
├── utils/                    # 工具模块
│   ├── logger.py             # 日志配置
│   ├── file_handler.py       # 文件处理
│   └── validators.py         # 验证器
│
├── outputs/                  # 输出文件目录
├── logs/                     # 日志文件
├── main.py                   # 应用入口
├── requirements.txt          # 依赖清单
└── README.md                 # 项目说明
```

## 🔧 高级配置

### 自定义模型路径

```python
# 在 app/config.py 中修改
WHISPER_MODEL = "medium"  # 更改为其他模型
```

### 修改文件大小限制

```python
# 在 app/config.py 中修改
MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 1GB
```

### 启用AI功能

确保在 `.env` 文件中配置了API密钥：

```bash
OPENAI_API_KEY=sk-xxx...
# 或
DEEPSEEK_API_KEY=sk-xxx...
```

## 📝 API文档

### 上传文件

```http
POST /upload
Content-Type: multipart/form-data

Response:
{
    "success": true,
    "task_id": "abc123",
    "filename": "video.mp4",
    "message": "文件上传成功"
}
```

### 开始转写

```http
POST /api/transcribe
Content-Type: application/json

{
    "task_id": "abc123",
    "language": "zh",
    "model": "base"
}

Response:
{
    "success": true,
    "task_id": "abc123",
    "message": "转写完成"
}
```

### 查询任务状态

```http
GET /api/task/{task_id}

Response:
{
    "success": true,
    "task_id": "abc123",
    "status": "completed",
    "progress": 100,
    "message": "转写完成"
}
```

### 获取结果

```http
GET /api/result/{task_id}

Response:
{
    "success": true,
    "task_id": "abc123",
    "text": "转写的文本内容...",
    "download_links": {
        "txt": "/api/download/abc123/txt"
    }
}
```

## 🐛 常见问题

### Q: 提示 "FFmpeg not found"

**A:** 请确保已安装FFmpeg并添加到系统PATH环境变量。

### Q: 转写速度很慢

**A:** 
- 使用更小的模型（如 `tiny` 或 `base`）
- 确保有足够的内存
- 考虑使用GPU加速（需安装CUDA）

### Q: 内存不足错误

**A:**
- 使用更小的模型
- 处理较小的文件
- 增加系统内存

### Q: AI功能不可用

**A:** 
- 检查 `.env` 文件中的API密钥配置
- 确保网络连接正常
- 检查API额度是否充足

## 🔐 安全建议

- **生产环境**：修改 `SECRET_KEY` 为强随机密钥
- **API密钥**：不要将 `.env` 文件提交到版本控制
- **文件验证**：系统已内置文件类型和大小验证
- **HTTPS**：生产环境建议使用HTTPS

## 🚀 部署指南

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### 使用 Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
```

```bash
docker build -t video-to-text .
docker run -p 5000:5000 -v $(pwd)/outputs:/app/outputs video-to-text
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，欢迎联系。

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 强大的语音识别模型
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [MoviePy](https://zulko.github.io/moviepy/) - 视频处理库
- [Bootstrap](https://getbootstrap.com/) - UI框架

---

**⭐ 如果这个项目对你有帮助，请给个星标支持一下！**
