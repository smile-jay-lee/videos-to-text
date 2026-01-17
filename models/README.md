# Whisper 模型文件夹

此目录用于存储 Whisper 语音识别模型（已配置为D盘项目目录，不占用C盘空间）。

## 推荐模型

中文转录推荐使用以下模型：

| 模型 | 大小 | 准确度 | 推荐场景 |
|------|------|--------|---------|
| `base` | ~142MB | ⭐⭐⭐ | 测试使用 |
| `small` | ~466MB | ⭐⭐⭐⭐ | **日常中文转录（推荐）** |
| `medium` | ~1.5GB | ⭐⭐⭐⭐⭐ | **高质量中文转录（推荐）** |

## 下载方式

### 方法1：可靠下载工具（推荐）✨

支持断点续传和自动重试，网络不稳定也能完整下载：

```bash
cd backend
python download_model_reliable.py
```

### 方法2：简单下载工具

```bash
cd backend
python download_model.py
```

根据提示选择要下载的模型（推荐选择 3-small 或 4-medium）

### 方法2：手动下载（适合网络不稳定）

使用浏览器或下载工具（迅雷、IDM等）下载以下文件到本目录：

**Small 模型** (推荐日常使用)
- 文件名：`small.pt`
- 下载链接：https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt
- 大小：~466MB
- SHA256：`9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794`

**Medium 模型** (推荐高质量)
- 文件名：`medium.pt`
- 下载链接：https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt
- 大小：~1.5GB
- SHA256：`345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1`

### 方法3：首次运行时自动下载

直接启动应用并选择模型，系统会自动下载到此目录：

```bash
cd backend
python main.py
```

## 注意事项

- 模型文件较大，首次下载需要时间，请耐心等待
- 下载完成后会自动缓存，之后使用无需重复下载
- 如果下载失败，可以删除未完成的`.pt`文件重试
- 手动下载时，请确保文件名为 `small.pt` 或 `medium.pt`

