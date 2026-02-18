# B站音频下载器使用指南

## 功能特点

✅ **零外部依赖**（仅需 `requests` 库）  
✅ **单文件运行**（所有逻辑内联）  
✅ **无需登录**（仅支持公开视频）  
✅ **自动重试**（主URL + 备用URL）  
✅ **支持分P**（多分P视频可选择下载）  
✅ **中文友好**（文件名正确处理Unicode）  

---

## 安装依赖

```bash
pip install requests
```

---

## 使用方法

### 1. 基础用法

```bash
# 通过 BV 号下载
python bili_downloader.py BV1xx411c7XD

# 通过完整 URL 下载
python bili_downloader.py https://www.bilibili.com/video/BV1xx411c7XD

# 通过短链接下载
python bili_downloader.py https://b23.tv/xxxxx
```

### 2. 下载指定分P

```bash
# 只下载第 2 分P
python bili_downloader.py BV1xx411c7XD 2

# 只下载第 1 分P
python bili_downloader.py https://www.bilibili.com/video/BV1xx411c7XD 1
```

### 3. 编程调用

```python
from bili_downloader import BiliDownloader

# 创建下载器实例
downloader = BiliDownloader(output_dir='my_audios')

# 下载所有分P
downloader.download_audio('BV1xx411c7XD')

# 只下载第3分P
downloader.download_audio('BV1xx411c7XD', page_num=3)
```

---

## 输出说明

### 目录结构

```
downloads/
├── 视频标题.m4a              # 单P视频
├── 视频标题_P1_分P标题.m4a   # 多P视频第1P
└── 视频标题_P2_分P标题.m4a   # 多P视频第2P
```

### 文件格式

- **纯音频流**: `.m4a` 格式（推荐，体积小）
- **完整视频**: `.mp4` 格式（少数视频不支持单独音频流时）

---

## 技术原理

### API 调用流程

```
1. 解析输入 → 提取 BV/AV 号
   ↓
2. 获取视频信息 (api.bilibili.com/x/web-interface/view)
   → 返回: aid, cid, title, pages
   ↓
3. 获取播放地址 (api.bilibili.com/x/player/playurl)
   → 参数: aid, cid, fnval=16 (DASH格式)
   → 返回: audio.baseUrl (音频流)
   ↓
4. 下载二进制流
   → 带自定义 Referer/User-Agent
```

### 关键参数

| 参数 | 值 | 说明 |
|------|---|------|
| `qn` | 64 | 未登录时的默认画质 |
| `fnval` | 16 | 请求 DASH 格式（分离音视频流） |
| `fnver` | 0 | 固定值 |
| `fourk` | 1 | 支持4K（即使未登录） |

### Headers 配置

```python
{
    'User-Agent': 'Chrome/132.0.0.0',
    'Referer': 'https://www.bilibili.com/',
    'Origin': 'https://www.bilibili.com',
}
```

---

## 常见问题

### 1. 为什么有些视频下载的是 `.mp4` 而不是 `.m4a`？

部分老视频或特殊视频不支持 DASH 格式的分离音频流，此时会下载完整的 MP4 文件（包含视频）。  
**解决方法**: 可使用 `ffmpeg` 提取音频：

```bash
ffmpeg -i input.mp4 -vn -acodec copy output.m4a
```

### 2. 下载失败提示 `-404` 或 `-403`

**可能原因**:
- 视频被删除/下架
- 视频需要付费（大会员专享）
- 视频需要登录观看

**解决方法**: 该脚本仅支持**公开、免费视频**，付费或限制视频无法下载。

### 3. 文件名乱码

脚本已处理中文 Unicode 编码，如遇问题请检查：
- 终端是否支持 UTF-8
- Windows 用户确保使用 PowerShell 或 CMD（UTF-8模式）

### 4. 下载速度慢

**可能原因**:
- 网络连接不稳定
- CDN 节点选择不佳

**解决方法**:
- 多次尝试（脚本会自动尝试备用URL）
- 检查网络连接

---

## 限制说明

⚠️ **本脚本仅支持以下场景**:

| 支持 ✅ | 不支持 ❌ |
|---------|----------|
| 公开视频 | 付费视频（大会员） |
| 免费视频 | 需登录视频 |
| 单P/多P | 番剧/影视 |
| BV/AV 号 | 直播回放 |

---

## 集成到主项目

如需集成到你的 Whisper 转录工具：

```python
# 在 main.py 中
from bili_downloader import BiliDownloader

def download_bili_audio(url):
    """下载B站音频并返回本地路径"""
    downloader = BiliDownloader(output_dir='temp_downloads')
    video_id = downloader.parse_video_url(url)
    video_info = downloader.get_video_info(video_id)
    
    if video_info:
        audio_info = downloader.get_audio_url(video_info['aid'], video_info['cid'])
        output_path = f"temp_downloads/{video_info['title']}.m4a"
        
        if downloader.download_file(audio_info['url'], output_path):
            return output_path
    
    return None

# 集成到转录流程
audio_path = download_bili_audio('BV1xx411c7XD')
if audio_path:
    transcribe(audio_path)
```

---

## 许可说明

- 本脚本仅供**学习研究**使用
- 请遵守B站用户协议和版权法规
- 下载内容仅限个人使用，禁止商业用途

---

## 更新日志

### v1.0 (2026-02-18)
- ✨ 初始版本
- ✅ 支持 BV/AV 号解析
- ✅ 支持多分P视频
- ✅ 自动重试机制
- ✅ 中文文件名处理
