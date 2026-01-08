# 语音转文字Web应用 - Python架构设计

**版本**: v1.0  
**日期**: 2026年1月8日  
**架构风格**: 三层架构 + MVC模式

---

## 一、整体架构设计

### 1.1 架构图

```
┌───────────────────────────────────────────────────────────────┐
│                        用户界面层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  上传页面    │  │  处理页面    │  │  结果页面    │           │
│  │ (upload)    │  │ (process)   │  │ (result)    │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└───────────────────────────────┬───────────────────────────────┘
                                │ HTTP/WebSocket
┌───────────────────────────────┴───────────────────────────────┐
│                     Flask应用层 (app/)                          │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  routes.py - 路由控制                                 │     │
│  │  ├─ GET  /          → 主页                           │     │
│  │  ├─ POST /upload    → 文件上传                       │     │
│  │  ├─ POST /transcribe → 转写任务                      │     │
│  │  ├─ GET  /status/:id → 任务状态                      │     │
│  │  └─ GET  /result/:id → 获取结果                      │     │
│  └──────────────────────────────────────────────────────┘     │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  config.py - 配置管理                                 │     │
│  │  └─ 环境变量、模型配置、文件路径等                    │     │
│  └──────────────────────────────────────────────────────┘     │
└───────────────────────────────┬───────────────────────────────┘
                                │
┌───────────────────────────────┴───────────────────────────────┐
│                    业务逻辑层 (services/)                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │ AudioService    │  │TranscriptService│  │ TextService  │  │
│  │ 音频处理服务     │  │  转写服务        │  │ 文本处理服务 │  │
│  │                 │  │                 │  │              │  │
│  │ • 提取音频      │  │ • 调用Whisper   │  │ • AI润色     │  │
│  │ • 格式转换      │  │ • 分段处理      │  │ • 生成总结   │  │
│  │ • 分割音频      │  │ • 结果合并      │  │ • 导出文件   │  │
│  └────────┬────────┘  └────────┬────────┘  └──────┬───────┘  │
└───────────┼────────────────────┼───────────────────┼──────────┘
            │                    │                   │
┌───────────┴────────────────────┴───────────────────┴──────────┐
│                     核心功能层 (core/)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐         │
│  │AudioExtractor│  │WhisperEngine │  │AIProcessor  │         │
│  │              │  │              │  │             │         │
│  │• moviepy集成 │  │• 模型加载    │  │• OpenAI API │         │
│  │• pydub集成   │  │• 转写执行    │  │• DeepSeek   │         │
│  └──────────────┘  │• 多模型支持  │  └─────────────┘         │
│                    └──────────────┘                           │
│  ┌──────────────┐  ┌──────────────┐                          │
│  │VideoDownloader│  │TaskManager   │                          │
│  │              │  │              │                          │
│  │• 抖音下载    │  │• 任务队列    │                          │
│  │• 通用下载    │  │• 进度跟踪    │                          │
│  └──────────────┘  └──────────────┘                          │
└───────────────────────────────┬───────────────────────────────┘
                                │
┌───────────────────────────────┴───────────────────────────────┐
│                     工具层 (utils/)                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │  logger    │  │file_handler│  │ validators │              │
│  │  日志管理   │  │  文件处理   │  │  验证工具   │              │
│  └────────────┘  └────────────┘  └────────────┘              │
└───────────────────────────────────────────────────────────────┘
```

---

## 二、核心模块设计

### 2.1 Core Layer (核心功能层)

#### 2.1.1 AudioExtractor (音频提取器)

```python
class AudioExtractor:
    """音频提取和处理核心类"""
    
    def extract_from_video(video_path: str, output_path: str) -> str:
        """从视频提取音频"""
        
    def convert_format(input_path: str, output_format: str) -> str:
        """转换音频格式"""
        
    def split_audio(audio_path: str, chunk_duration: int) -> List[str]:
        """分割大音频文件"""
        
    def get_audio_info(audio_path: str) -> dict:
        """获取音频信息（时长、格式、大小等）"""
```

#### 2.1.2 WhisperEngine (Whisper引擎)

```python
class WhisperEngine:
    """Whisper转写引擎"""
    
    def __init__(self, model_size: str = "base"):
        """初始化并加载模型"""
        
    def transcribe(audio_path: str, language: str = "zh") -> dict:
        """转写单个音频文件"""
        
    def transcribe_chunks(chunks: List[str], language: str = "zh") -> str:
        """转写多个音频片段并合并"""
        
    def get_available_models() -> List[str]:
        """获取可用模型列表"""
```

#### 2.1.3 AIProcessor (AI文本处理器)

```python
class AIProcessor:
    """AI文本处理器（润色、总结）"""
    
    def __init__(self, provider: str = "openai", api_key: str = None):
        """初始化AI处理器"""
        
    def refine_text(text: str) -> str:
        """润色文本"""
        
    def summarize(text: str, max_length: int = 500) -> str:
        """生成摘要"""
        
    def process_long_text(text: str) -> dict:
        """处理长文本（分块处理）"""
```

#### 2.1.4 TaskManager (任务管理器)

```python
class TaskManager:
    """异步任务管理"""
    
    def create_task(task_type: str, params: dict) -> str:
        """创建新任务，返回任务ID"""
        
    def get_task_status(task_id: str) -> dict:
        """获取任务状态和进度"""
        
    def update_progress(task_id: str, progress: int, message: str):
        """更新任务进度"""
        
    def complete_task(task_id: str, result: dict):
        """标记任务完成"""
```

---

### 2.2 Service Layer (业务逻辑层)

#### 2.2.1 AudioService (音频服务)

```python
class AudioService:
    """音频处理业务逻辑"""
    
    def __init__(self):
        self.extractor = AudioExtractor()
        
    def process_video(video_path: str, task_id: str = None) -> str:
        """
        处理视频文件
        1. 验证视频文件
        2. 提取音频
        3. 检查音频大小
        4. 必要时分割音频
        返回: 音频文件路径或音频片段列表
        """
        
    def process_audio(audio_path: str) -> dict:
        """处理音频文件，返回音频信息"""
```

#### 2.2.2 TranscriptionService (转写服务)

```python
class TranscriptionService:
    """转写业务逻辑"""
    
    def __init__(self, model_size: str = "base"):
        self.engine = WhisperEngine(model_size)
        self.task_manager = TaskManager()
        
    def transcribe_file(file_path: str, language: str = "zh", 
                       task_id: str = None) -> dict:
        """
        转写文件
        1. 判断是视频还是音频
        2. 处理音频（分割大文件）
        3. 调用Whisper转写
        4. 更新进度
        返回: {text: str, segments: list, language: str}
        """
        
    def transcribe_url(url: str, language: str = "zh") -> dict:
        """从URL下载并转写"""
```

#### 2.2.3 TextService (文本处理服务)

```python
class TextService:
    """文本处理业务逻辑"""
    
    def __init__(self, ai_provider: str = None):
        self.processor = AIProcessor(ai_provider) if ai_provider else None
        
    def refine_and_summarize(text: str) -> dict:
        """
        润色和总结文本
        返回: {refined: str, summary: str}
        """
        
    def export_to_txt(text: str, output_path: str):
        """导出为TXT文件"""
        
    def export_to_srt(segments: list, output_path: str):
        """导出为SRT字幕文件"""
```

---

### 2.3 Application Layer (应用层)

#### 2.3.1 配置管理 (config.py)

```python
class Config:
    """应用配置"""
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    
    # 文件配置
    UPLOAD_FOLDER = 'static/uploads'
    OUTPUT_FOLDER = 'outputs'
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mp3', 'wav', 'm4a'}
    
    # Whisper配置
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
    WHISPER_LANGUAGE = 'zh'
    
    # AI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    
    # 任务配置
    TASK_TIMEOUT = 3600  # 1小时
```

#### 2.3.2 路由设计 (routes.py)

```python
# 主要路由

GET  /                          # 主页
GET  /upload                    # 上传页面
POST /api/upload                # 上传文件API
POST /api/transcribe            # 开始转写
GET  /api/task/<task_id>        # 获取任务状态
GET  /api/result/<task_id>      # 获取转写结果
POST /api/process-text          # 文本处理（润色/总结）
GET  /api/download/<file_id>    # 下载结果文件
```

---

## 三、数据流设计

### 3.1 完整处理流程

```
用户上传文件
    ↓
验证文件 (validators)
    ↓
保存到临时目录 (file_handler)
    ↓
创建任务 (TaskManager)
    ↓
[异步处理开始]
    ↓
提取/处理音频 (AudioService)
    ↓
分割音频（如果需要）(AudioExtractor)
    ↓
Whisper转写 (TranscriptionService)
    ↓
[可选] AI文本处理 (TextService)
    ↓
保存结果
    ↓
清理临时文件
    ↓
标记任务完成
    ↓
用户查看/下载结果
```

### 3.2 任务状态管理

```python
TaskStatus = {
    'PENDING': '等待处理',
    'PROCESSING': '处理中',
    'TRANSCRIBING': '转写中',
    'REFINING': 'AI处理中',
    'COMPLETED': '已完成',
    'FAILED': '失败',
    'CANCELLED': '已取消'
}
```

---

## 四、目录结构详细说明

```
video-to-text/
│
├── app/                          # Flask应用
│   ├── __init__.py               # 应用工厂
│   ├── config.py                 # 配置类
│   ├── routes.py                 # 路由定义
│   ├── models.py                 # 数据模型（可选，用于数据库）
│   │
│   ├── templates/                # HTML模板
│   │   ├── base.html             # 基础模板
│   │   ├── index.html            # 主页
│   │   ├── upload.html           # 上传页
│   │   ├── process.html          # 处理进度页
│   │   └── result.html           # 结果展示页
│   │
│   └── static/                   # 静态文件
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   ├── upload.js         # 上传逻辑
│       │   └── progress.js       # 进度更新
│       └── uploads/              # 上传文件临时存储
│
├── core/                         # 核心功能
│   ├── __init__.py
│   ├── audio_extractor.py        # 音频提取器
│   ├── whisper_engine.py         # Whisper引擎
│   ├── ai_processor.py           # AI处理器
│   ├── video_downloader.py       # 视频下载器
│   └── task_manager.py           # 任务管理器
│
├── services/                     # 业务逻辑
│   ├── __init__.py
│   ├── audio_service.py          # 音频服务
│   ├── transcription_service.py  # 转写服务
│   └── text_service.py           # 文本服务
│
├── utils/                        # 工具模块
│   ├── __init__.py
│   ├── logger.py                 # 日志配置
│   ├── file_handler.py           # 文件操作
│   ├── validators.py             # 验证器
│   └── helpers.py                # 辅助函数
│
├── outputs/                      # 输出文件目录
│   ├── transcriptions/           # 转写文本
│   ├── summaries/                # 摘要文件
│   └── subtitles/                # 字幕文件
│
├── tests/                        # 测试文件
│   ├── test_core/
│   ├── test_services/
│   └── test_utils/
│
├── docs/                         # 文档
│   ├── API.md                    # API文档
│   └── DEPLOYMENT.md             # 部署文档
│
├── logs/                         # 日志文件
│
├── .env.example                  # 环境变量模板
├── .gitignore
├── requirements.txt              # 依赖清单
├── README.md                     # 项目说明
└── main.py                       # 应用入口
```

---

## 五、关键技术决策

### 5.1 异步任务处理

**方案选择**: 
- **初期**: Threading (简单快速)
- **扩展**: Celery + Redis (生产环境)

**原因**:
- Whisper转写是CPU密集型任务
- 需要避免阻塞Web请求
- 需要进度跟踪和任务管理

### 5.2 文件存储策略

```python
# 临时文件：保留1小时后自动清理
/static/uploads/{task_id}/input.{ext}

# 处理中文件：
/static/uploads/{task_id}/audio.mp3
/static/uploads/{task_id}/chunks/

# 最终结果：保留7天
/outputs/transcriptions/{task_id}.txt
/outputs/summaries/{task_id}_summary.txt
```

### 5.3 进度跟踪机制

使用WebSocket或轮询方式实时更新：

```python
progress_data = {
    'task_id': 'xxx',
    'status': 'TRANSCRIBING',
    'progress': 45,  # 0-100
    'message': '正在转写第3/5段音频...',
    'current_step': 'transcription',
    'total_steps': 4
}
```

---

## 六、API设计规范

### 6.1 RESTful API接口

#### 上传文件
```http
POST /api/upload
Content-Type: multipart/form-data

Response:
{
    "success": true,
    "task_id": "abc123",
    "message": "文件上传成功"
}
```

#### 开始转写
```http
POST /api/transcribe
Content-Type: application/json
{
    "task_id": "abc123",
    "language": "zh",
    "model": "base",
    "enable_ai": true
}

Response:
{
    "success": true,
    "task_id": "abc123",
    "estimated_time": 300
}
```

#### 查询任务状态
```http
GET /api/task/abc123

Response:
{
    "task_id": "abc123",
    "status": "TRANSCRIBING",
    "progress": 65,
    "message": "正在转写...",
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": "2026-01-08T10:05:00Z"
}
```

#### 获取结果
```http
GET /api/result/abc123

Response:
{
    "task_id": "abc123",
    "text": "转写文本内容...",
    "refined_text": "润色后的文本...",
    "summary": "摘要内容...",
    "download_links": {
        "txt": "/api/download/abc123.txt",
        "srt": "/api/download/abc123.srt"
    }
}
```

---

## 七、性能优化策略

### 7.1 模型预加载
```python
# 应用启动时预加载Whisper模型
@app.before_first_request
def preload_models():
    global whisper_model
    whisper_model = whisper.load_model(Config.WHISPER_MODEL)
```

### 7.2 音频处理优化
- 使用多进程处理音频分段
- 压缩临时文件
- 智能分割策略（按静音点分割）

### 7.3 缓存策略
- 相同文件MD5检测，避免重复处理
- 结果缓存7天

---

## 八、安全性设计

### 8.1 文件验证
```python
def validate_file(file):
    # 检查文件扩展名
    # 检查MIME类型
    # 检查文件大小
    # 病毒扫描（可选）
```

### 8.2 API密钥保护
- 从环境变量读取
- 不在日志中记录
- 传输时加密

### 8.3 访问控制
- 任务ID使用UUID
- 文件访问权限验证
- 速率限制

---

## 九、部署建议

### 9.1 开发环境
```bash
python main.py
# 或
flask run --debug
```

### 9.2 生产环境
```bash
# 使用Gunicorn + Nginx
gunicorn -w 4 -b 127.0.0.1:5000 main:app

# Docker部署
docker build -t video-to-text .
docker run -p 5000:5000 video-to-text
```

### 9.3 依赖项
- Python 3.8+
- FFmpeg
- CUDA (可选，GPU加速)

---

## 十、监控与日志

### 10.1 日志级别
```python
# 使用Python logging模块
DEBUG: 详细调试信息
INFO: 一般信息（任务开始/完成）
WARNING: 警告（文件过大等）
ERROR: 错误（处理失败）
CRITICAL: 严重错误（系统故障）
```

### 10.2 监控指标
- 任务处理时间
- 成功/失败率
- 文件大小分布
- API调用次数

---

**总结**: 本架构设计遵循模块化、可扩展、易维护的原则，适合快速开发和后续迭代。
