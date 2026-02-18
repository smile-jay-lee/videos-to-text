# BiliAudioService 模块说明

## 📦 新增文件

### 核心服务
```
backend/services/bili_service.py         # Bilibili音频下载服务（540行）
```

### 测试文件
```
tests/test_bili_service.py               # 完整功能测试
tests/test_bili_service_quick.py         # 快速验证测试
```

### 文档
```
docs/BiliAudioService集成指南.md         # 详细集成文档
```

---

## 🎯 模块特性

### 1. 零外部依赖
- 仅使用 Python 标准库 + `requests`
- 不依赖 `bilitools` 或其他第三方库
- 所有逻辑独立实现

### 2. 低耦合设计
- 独立的服务模块
- 不影响现有代码
- 可选择性使用

### 3. 完整功能
- ✅ 解析多种URL格式（BV/AV/短链接）
- ✅ 获取视频元数据
- ✅ 下载DASH音频流
- ✅ 支持多分P视频
- ✅ 自动重试和备用URL
- ✅ 安全文件名处理
- ✅ 返回绝对路径

### 4. 集成友好
- 统一的日志系统
- 清晰的错误处理
- 类型提示完整
- 详细的文档注释

---

## 🚀 快速使用

### 基础示例

```python
from services import BiliAudioService

# 初始化
service = BiliAudioService()

# 下载音频
audio_path = service.download_audio('BV1xx411c7XD')

if audio_path:
    print(f"✓ 下载成功: {audio_path}")
    # 传给 Whisper 转录
```

### 集成到转录流程

```python
from services import BiliAudioService, TranscriptionService

# 下载B站音频
bili_service = BiliAudioService()
audio_path = bili_service.download_audio('BV1xx411c7XD')

# Whisper 转录
transcription_service = TranscriptionService(model_size='small')
result = transcription_service.transcribe_file(audio_path, language='zh')

print(result['text'])
```

---

## 📋 核心方法

### BiliAudioService

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `download_audio(url, page_num)` | 下载音频 | 音频文件绝对路径 |
| `get_video_info(url)` | 获取视频信息 | 视频元数据字典 |

### 私有方法（供内部使用）

| 方法 | 说明 |
|------|------|
| `_parse_video_url()` | 解析URL，提取ID |
| `_get_video_info()` | 调用B站API获取信息 |
| `_get_audio_url()` | 获取音频流URL |
| `_download_file()` | 下载文件（支持重试） |
| `_generate_filename()` | 生成安全文件名 |

---

## 🔗 技术实现

### API调用流程

```
1. 解析URL → 提取 BV/AV 号
   ↓
2. GET /x/web-interface/view
   → 返回: aid, cid, pages[]
   ↓
3. GET /x/player/playurl
   → 参数: aid, cid, fnval=16
   → 返回: dash.audio[].baseUrl
   ↓
4. 下载音频流
   → 使用 Referer/User-Agent
   → 支持备用URL和重试
   ↓
5. 保存到 temp_audio/
   → 返回绝对路径
```

### 关键参数

| 参数 | 值 | 说明 |
|------|---|------|
| `fnval` | 16 | DASH格式（分离音视频） |
| `qn` | 64 | 未登录默认质量 |
| `User-Agent` | Chrome/132 | 防爬必需 |
| `Referer` | bilibili.com | 防爬必需 |

---

## 📊 文件结构

```
backend/
  services/
    __init__.py              # 已更新：添加 BiliAudioService
    bili_service.py          # 新增：核心服务
    transcription_service.py # 现有：转录服务
    text_service.py          # 现有：文本服务

tests/
  test_bili_service.py       # 新增：完整测试
  test_bili_service_quick.py # 新增：快速测试

docs/
  BiliAudioService集成指南.md # 新增：集成文档

temp_audio/                  # 新增：默认输出目录（自动创建）
```

---

## ✅ 测试验证

### 运行快速测试

```bash
python tests/test_bili_service_quick.py
```

**预期输出**:
```
✓ 初始化成功
✓ URL解析功能测试通过
✓ 文件名生成测试通过
```

### 运行完整测试（需要网络）

```bash
python tests/test_bili_service.py
```

**测试项目**:
1. URL解析和视频信息获取
2. 音频下载功能
3. 完整流程演示（下载+模拟转录）
4. 查看使用示例代码

---

## 🔧 配置选项

### 自定义输出目录

```python
service = BiliAudioService(output_dir='custom_dir')
```

### 调整超时和重试

在 `bili_service.py` 中修改类常量：

```python
class BiliAudioService:
    TIMEOUT = 30           # 请求超时（秒）
    MAX_RETRIES = 3        # 最大重试次数
    DEFAULT_OUTPUT_DIR = 'temp_audio'  # 默认输出目录
```

---

## ⚠️ 注意事项

### 支持的视频类型

| 类型 | 支持 |
|------|------|
| 公开普通视频 | ✅ |
| 多分P视频 | ✅ |
| 短链接 | ✅ |
| 付费视频（大会员） | ❌ |
| 需登录视频 | ❌ |
| 番剧/影视 | ❌ |

### 文件格式

- 优先下载：`.m4a`（纯音频流）
- 降级方案：`.mp4`（包含视频的完整文件）

---

## 🆕 更新日志

### v1.0 (2026-02-18)

**新增功能**:
- ✨ BiliAudioService 核心服务
- ✨ URL解析（支持BV/AV/短链接）
- ✨ 视频信息获取
- ✨ DASH音频流下载
- ✨ 多分P视频支持
- ✨ 自动重试机制
- ✨ 安全文件名处理

**技术特性**:
- 📦 零外部依赖（仅 requests）
- 🔗 低耦合设计
- 📝 完整日志集成
- 🛡️ 完善错误处理
- 📚 详细文档和测试

---

## 📚 相关文档

- [集成指南](../docs/BiliAudioService集成指南.md) - 详细的集成文档
- [测试脚本](../tests/test_bili_service.py) - 功能测试
- [主项目文档](../README.md) - 项目总览

---

## 💡 使用建议

### 1. 在API路由中使用

推荐在 `backend/app/api_routes.py` 中添加B站相关端点：

```python
@app.route('/api/bili/transcribe', methods=['POST'])
def bili_transcribe():
    # 使用 BiliAudioService + TranscriptionService
    pass
```

### 2. 创建服务编排层

创建 `VideoToTextService` 整合下载和转录：

```python
class VideoToTextService:
    def __init__(self):
        self.bili = BiliAudioService()
        self.transcription = TranscriptionService()
```

### 3. 添加后台任务队列

对于大量请求，建议使用 Celery 等任务队列。

---

## 🤝 贡献

如需扩展功能，建议：

1. 在 `bili_service.py` 中添加新方法
2. 保持低耦合原则
3. 添加相应的测试
4. 更新文档

---

更新时间: 2026-02-18  
版本: v1.0  
维护者: AI Assistant
