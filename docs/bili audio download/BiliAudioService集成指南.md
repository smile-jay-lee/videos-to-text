# BiliAudioService 集成指南

## 📋 概述

`BiliAudioService` 是一个独立的 Bilibili 音频下载服务模块，专为本地视频转文字项目设计。

**核心特性**:
- ✅ **零外部依赖**: 仅需 `requests` 库
- ✅ **低耦合设计**: 独立模块，不影响现有代码
- ✅ **完整日志**: 集成项目 logger 系统
- ✅ **安全文件名**: 自动处理特殊字符和中文
- ✅ **返回绝对路径**: 便于后续 Whisper 转录

---

## 🚀 快速开始

### 1. 基础使用

```python
from services import BiliAudioService

# 初始化服务
service = BiliAudioService()

# 下载音频（返回绝对路径）
audio_path = service.download_audio('BV1xx411c7XD')

if audio_path:
    print(f"音频已保存: {audio_path}")
    # 继续处理...
```

### 2. 指定分P下载

```python
service = BiliAudioService()

# 下载第2分P
audio_path = service.download_audio('BV1xx411c7XD', page_num=2)
```

### 3. 自定义输出目录

```python
# 使用自定义目录
service = BiliAudioService(output_dir='custom_audio')
audio_path = service.download_audio('BV1xx411c7XD')
```

---

## 🔗 集成到转录流程

### 方案 A: 在 API 路由中集成

**文件**: `backend/app/api_routes.py`

```python
from flask import Blueprint, request, jsonify
from services import BiliAudioService, TranscriptionService

api = Blueprint('api', __name__)

@api.route('/api/bili/transcribe', methods=['POST'])
def transcribe_bili_video():
    """
    B站视频转文字接口
    
    请求体:
    {
        "url": "BV1xx411c7XD",
        "page": 1,  # 可选
        "model": "small",  # 可选
        "language": "zh"  # 可选
    }
    """
    try:
        data = request.get_json()
        url = data.get('url')
        page_num = data.get('page')
        model = data.get('model', 'small')
        language = data.get('language', 'zh')
        
        # 验证参数
        if not url:
            return jsonify({'error': '缺少 url 参数'}), 400
        
        # 步骤1: 下载音频
        bili_service = BiliAudioService()
        audio_path = bili_service.download_audio(url, page_num=page_num)
        
        if not audio_path:
            return jsonify({'error': '音频下载失败'}), 500
        
        # 步骤2: 转录
        transcription_service = TranscriptionService(model_size=model)
        result = transcription_service.transcribe_file(
            audio_path,
            language=language
        )
        
        # 步骤3: 返回结果
        return jsonify({
            'success': True,
            'text': result['text'],
            'segments': result['segments'],
            'audio_path': audio_path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/api/bili/info', methods=['GET'])
def get_bili_video_info():
    """
    获取B站视频信息接口（不下载）
    
    参数:
        url: 视频URL或BV号
    """
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': '缺少 url 参数'}), 400
    
    service = BiliAudioService()
    info = service.get_video_info(url)
    
    if info:
        return jsonify({
            'success': True,
            'data': info
        })
    else:
        return jsonify({'error': '获取视频信息失败'}), 500
```

### 方案 B: 创建专门的服务编排层

**文件**: `backend/services/video_to_text_service.py`

```python
"""
视频转文字服务编排层
整合下载和转录功能
"""

from typing import Optional, Dict
from pathlib import Path
from .bili_service import BiliAudioService
from .transcription_service import TranscriptionService
from utils.logger import get_logger
from utils.file_handler import cleanup_file

logger = get_logger(__name__)


class VideoToTextService:
    """视频转文字服务（整合B站下载+Whisper转录）"""
    
    def __init__(self, model_size: str = "small"):
        self.bili_service = BiliAudioService()
        self.transcription_service = TranscriptionService(model_size)
        logger.info("视频转文字服务已初始化")
    
    def process_bili_video(
        self,
        url: str,
        page_num: Optional[int] = None,
        language: str = "zh",
        cleanup_audio: bool = True
    ) -> Optional[Dict]:
        """
        处理B站视频：下载 -> 转录
        
        Args:
            url: B站视频URL或BV号
            page_num: 指定分P
            language: 语言代码
            cleanup_audio: 是否在转录后删除音频文件
            
        Returns:
            {
                'text': str,
                'segments': list,
                'video_info': dict,
                'audio_path': str  # 如果 cleanup_audio=False
            }
        """
        audio_path = None
        
        try:
            # 1. 获取视频信息
            logger.info(f"开始处理B站视频: {url}")
            video_info = self.bili_service.get_video_info(url)
            
            if not video_info:
                logger.error("无法获取视频信息")
                return None
            
            # 2. 下载音频
            logger.info("下载音频...")
            audio_path = self.bili_service.download_audio(url, page_num)
            
            if not audio_path:
                logger.error("音频下载失败")
                return None
            
            logger.info(f"音频已保存: {audio_path}")
            
            # 3. 转录
            logger.info("开始转录...")
            transcription_result = self.transcription_service.transcribe_file(
                audio_path,
                language=language
            )
            
            # 4. 组装结果
            result = {
                'text': transcription_result['text'],
                'segments': transcription_result['segments'],
                'video_info': {
                    'title': video_info['title'],
                    'owner': video_info['owner'],
                    'bvid': video_info['bvid'],
                },
            }
            
            # 5. 清理音频文件（可选）
            if cleanup_audio and audio_path:
                cleanup_file(audio_path)
                logger.info("已清理临时音频文件")
            else:
                result['audio_path'] = audio_path
            
            logger.info("处理完成")
            return result
            
        except Exception as e:
            logger.error(f"处理过程发生异常: {e}", exc_info=True)
            
            # 清理可能的残留文件
            if audio_path and Path(audio_path).exists():
                cleanup_file(audio_path)
            
            return None
```

---

## 📝 使用示例

### 示例 1: 命令行工具

```python
# examples/bili_to_text_cli.py
from services import BiliAudioService
from core import WhisperEngine

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python bili_to_text_cli.py <BV号>")
        return
    
    url = sys.argv[1]
    
    # 下载
    print("下载音频...")
    service = BiliAudioService()
    audio_path = service.download_audio(url)
    
    if not audio_path:
        print("下载失败")
        return
    
    # 转录
    print("转录中...")
    engine = WhisperEngine(model_name='small')
    result = engine.transcribe(audio_path)
    
    print("\n转录结果:")
    print(result['text'])

if __name__ == '__main__':
    main()
```

### 示例 2: 批量处理

```python
# 批量处理多分P视频
from services import BiliAudioService
from core import WhisperEngine

def batch_process_video(bvid):
    service = BiliAudioService()
    engine = WhisperEngine(model_name='small')
    
    # 获取视频信息
    info = service.get_video_info(bvid)
    if not info:
        return
    
    print(f"视频: {info['title']}")
    print(f"总分P: {len(info['pages'])}")
    
    # 逐个处理
    for page in info['pages']:
        print(f"\n处理 P{page['page']}: {page['title']}")
        
        # 下载
        audio_path = service.download_audio(bvid, page_num=page['page'])
        if not audio_path:
            continue
        
        # 转录
        result = engine.transcribe(audio_path)
        
        # 保存
        output_file = f"output_P{page['page']}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        
        print(f"✓ 已保存: {output_file}")

# 使用
batch_process_video('BV1xx411c7XD')
```

---

## 🛠️ API 接口设计

### 端点 1: 下载音频

```
POST /api/bili/download
Content-Type: application/json

{
    "url": "BV1xx411c7XD",
    "page": 1  // 可选
}

Response:
{
    "success": true,
    "audio_path": "/path/to/audio.m4a"
}
```

### 端点 2: 一键转录

```
POST /api/bili/transcribe
Content-Type: application/json

{
    "url": "BV1xx411c7XD",
    "page": 1,      // 可选
    "model": "small",  // 可选
    "language": "zh"   // 可选
}

Response:
{
    "success": true,
    "text": "转录文本...",
    "segments": [...],
    "video_info": {
        "title": "视频标题",
        "owner": "UP主"
    }
}
```

### 端点 3: 获取视频信息

```
GET /api/bili/info?url=BV1xx411c7XD

Response:
{
    "success": true,
    "data": {
        "title": "视频标题",
        "owner": "UP主",
        "pages": [...]
    }
}
```

---

## 📊 前端集成示例

### React 组件

```jsx
import React, { useState } from 'react';

function BiliTranscriber() {
    const [url, setUrl] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleTranscribe = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/bili/transcribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            
            const data = await response.json();
            setResult(data);
        } catch (error) {
            console.error('转录失败:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <input 
                value={url}
                onChange={e => setUrl(e.target.value)}
                placeholder="输入B站视频URL或BV号"
            />
            <button onClick={handleTranscribe} disabled={loading}>
                {loading ? '处理中...' : '开始转录'}
            </button>
            
            {result && (
                <div>
                    <h3>{result.video_info.title}</h3>
                    <p>{result.text}</p>
                </div>
            )}
        </div>
    );
}
```

---

## ⚠️ 注意事项

### 1. 限制说明

- ✅ 支持：公开、免费视频
- ❌ 不支持：付费视频、需登录视频、番剧

### 2. 错误处理

服务已内置完善的错误处理和日志记录：

```python
audio_path = service.download_audio(url)
if not audio_path:
    # 下载失败，日志已记录
    return {"error": "下载失败"}
```

### 3. 文件清理

建议在转录完成后清理临时文件：

```python
from utils.file_handler import cleanup_file

audio_path = service.download_audio(url)
# ... 转录 ...
cleanup_file(audio_path)  # 清理
```

### 4. 并发控制

如需处理大量请求，建议使用队列：

```python
from queue import Queue
from threading import Thread

task_queue = Queue()

def worker():
    while True:
        url = task_queue.get()
        service.download_audio(url)
        task_queue.task_done()

# 启动工作线程
Thread(target=worker, daemon=True).start()
```

---

## 🧪 测试

### 运行测试

```bash
# 快速测试（无需网络）
python tests/test_bili_service_quick.py

# 完整测试（需要网络）
python tests/test_bili_service.py
```

### 单元测试示例

```python
import unittest
from services import BiliAudioService

class TestBiliAudioService(unittest.TestCase):
    
    def setUp(self):
        self.service = BiliAudioService()
    
    def test_parse_bvid(self):
        result = self.service._parse_video_url('BV1xx411c7XD')
        self.assertEqual(result['type'], 'bvid')
        self.assertEqual(result['id'], 'BV1xx411c7XD')
    
    def test_parse_url(self):
        url = 'https://www.bilibili.com/video/BV1xx411c7XD'
        result = self.service._parse_video_url(url)
        self.assertEqual(result['type'], 'bvid')
```

---

## 📚 相关文档

- [主项目 README](../README.md)
- [Whisper 转录服务](./transcription_service.py)
- [工具函数文档](../utils/README.md)

---

## 🔧 故障排查

### 问题 1: 下载失败 (HTTP 403)

**原因**: Headers 未正确设置  
**解决**: 服务已内置正确的 Headers，无需额外配置

### 问题 2: 无法识别URL

**原因**: URL格式不支持  
**解决**: 确保使用以下格式之一：
- `BV1xx411c7XD`
- `https://www.bilibili.com/video/BV1xx411c7XD`
- `https://b23.tv/xxxxx`

### 问题 3: 文件名乱码

**原因**: 编码问题  
**解决**: 服务已自动处理中文文件名，无需额外配置

---

更新日期: 2026-02-18
