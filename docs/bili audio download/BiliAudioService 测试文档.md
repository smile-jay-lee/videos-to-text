# BiliAudioService 测试文档

## 测试文件概览

本项目为 `BiliAudioService` 创建了三套完整的测试文件，覆盖不同的测试场景。

---

## 📁 测试文件

### 1. test_bili_service_unit.py ⭐
**类型**: 单元测试（使用 unittest + mock）  
**网络**: 不需要  
**用途**: 自动化测试，CI/CD 集成

#### 测试覆盖

| 测试类 | 测试数量 | 说明 |
|--------|---------|------|
| `TestBiliAudioServiceInit` | 3 | 初始化和配置 |
| `TestParseVideoUrl` | 8 | URL 解析功能 |
| `TestGenerateFilename` | 6 | 文件名生成 |
| `TestGetVideoInfoMocked` | 3 | 视频信息获取（Mock） |
| `TestGetAudioUrlMocked` | 3 | 音频流获取（Mock） |
| `TestDownloadFileMocked` | 2 | 文件下载（Mock） |
| `TestIntegration` | 1 | 集成测试 |
| `TestEdgeCases` | 3 | 边界情况 |
| **总计** | **29** | **全部通过 ✓** |

#### 运行方式

```bash
# 运行所有单元测试
python tests/test_bili_service_unit.py

# 使用 pytest（如果已安装）
pytest tests/test_bili_service_unit.py -v
```

#### 测试结果

```
✓ 运行测试: 29
✓ 成功: 29
✓ 失败: 0
✓ 错误: 0
```

---

### 2. test_bili_service_network.py 🌐
**类型**: 功能测试（真实网络请求）  
**网络**: 需要  
**用途**: 手动测试，验证实际功能

#### 测试项目

1. **URL 解析功能** (离线)
   - 测试各种 URL 格式
   - BV号、AV号、完整URL
   
2. **获取视频信息** (需要网络)
   - 验证 API 调用
   - 检查返回数据完整性
   
3. **下载音频功能** (需要网络)
   - 实际下载测试
   - 统计下载速度
   
4. **文件名生成** (离线)
   - 特殊字符处理
   - 长度限制
   
5. **错误处理** (需要网络)
   - 无效 BV 号
   - 无效 URL
   - 空字符串
   
6. **多分P视频** (需要网络)
   - 多分P解析
   - 特定分P选择

#### 运行方式

```bash
python tests/test_bili_service_network.py
```

#### 交互式测试

测试过程中会提示输入：
- 测试用的 BV 号或 URL
- 是否执行下载测试
- 是否清理测试文件

---

### 3. test_bili_service_quick.py ⚡
**类型**: 快速验证测试  
**网络**: 不需要  
**用途**: 快速验证基础功能

#### 测试内容

1. 服务初始化
2. URL 解析功能
3. 文件名生成

#### 运行方式

```bash
python tests/test_bili_service_quick.py
```

#### 特点

- 无依赖冲突
- 运行速度快
- 适合快速验证

---

## 🎯 测试覆盖率

### 核心功能覆盖

| 功能模块 | 单元测试 | 网络测试 | 快速测试 |
|---------|---------|---------|---------|
| 初始化 | ✓ | ✓ | ✓ |
| URL 解析 | ✓ | ✓ | ✓ |
| 视频信息获取 | ✓ (Mock) | ✓ (真实) | - |
| 音频流获取 | ✓ (Mock) | - | - |
| 文件下载 | ✓ (Mock) | ✓ (真实) | - |
| 文件名生成 | ✓ | ✓ | ✓ |
| 错误处理 | ✓ | ✓ | - |
| 多分P处理 | ✓ | ✓ | - |

### 方法覆盖

| 方法 | 覆盖 |
|------|------|
| `__init__()` | ✓ |
| `download_audio()` | ✓ |
| `get_video_info()` | ✓ |
| `_parse_video_url()` | ✓ |
| `_get_video_info()` | ✓ |
| `_get_audio_url()` | ✓ |
| `_download_file()` | ✓ |
| `_generate_filename()` | ✓ |

**覆盖率**: 100% ✓

---

## 🚀 快速开始

### 1. 运行所有单元测试（推荐）

```bash
python tests/test_bili_service_unit.py
```

**预期输出**:
```
✓ 运行测试: 29
✓ 成功: 29
✓ 失败: 0
```

### 2. 快速验证

```bash
python tests/test_bili_service_quick.py
```

### 3. 完整功能测试（需要网络）

```bash
python tests/test_bili_service_network.py
```

---

## 📊 测试详情

### 单元测试示例

#### 测试 URL 解析

```python
def test_parse_bvid(self):
    """测试解析 BV 号"""
    result = self.service._parse_video_url('BV1xx411c7XD')
    self.assertEqual(result['type'], 'bvid')
    self.assertEqual(result['id'], 'BV1xx411c7XD')
```

#### 测试文件名生成

```python
def test_title_with_special_chars(self):
    """测试包含特殊字符的标题"""
    result = self.service._generate_filename('标题<>:"|?*')
    self.assertNotIn('<', result)
    self.assertNotIn('>', result)
```

#### 测试 API 调用 (Mock)

```python
@patch('requests.Session.get')
def test_get_video_info_single_page(self, mock_get):
    """测试获取单P视频信息"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'code': 0,
        'data': {...}
    }
    mock_get.return_value = mock_response
    
    result = self.service._get_video_info(video_id)
    self.assertIsNotNone(result)
```

---

## 🔧 持续集成

### GitHub Actions 配置示例

```yaml
name: Test BiliAudioService

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install requests
    
    - name: Run unit tests
      run: |
        python tests/test_bili_service_unit.py
```

---

## 📝 测试最佳实践

### 1. 测试前准备

```bash
# 确保依赖已安装
pip install requests

# 创建测试环境
cd "d:\project\videos to text"
```

### 2. 测试顺序

1. 先运行 **快速测试** 验证基础功能
2. 再运行 **单元测试** 确保代码质量
3. 最后运行 **网络测试** 验证实际功能

### 3. 调试失败的测试

```bash
# 运行单个测试类
python -m unittest tests.test_bili_service_unit.TestParseVideoUrl

# 运行单个测试方法
python -m unittest tests.test_bili_service_unit.TestParseVideoUrl.test_parse_bvid

# 显示详细输出
python tests/test_bili_service_unit.py -v
```

---

## 🐛 常见问题

### 问题 1: 导入错误

**错误信息**:
```
ImportError: Numba needs NumPy 2.0 or less
```

**解决**: 测试文件已使用直接导入方式，绕过依赖冲突

### 问题 2: Mock 不工作

**原因**: Mock 的路径不正确

**解决**: 使用 `@patch('requests.Session.get')` 而不是 `@patch('bili_service.requests.Session.get')`

### 问题 3: 网络测试失败

**原因**: 
- 网络连接问题
- B站 API 临时不可用
- 测试视频被删除

**解决**: 使用其他公开视频进行测试

---

## 📈 测试报告

### 最近测试结果

**日期**: 2026-02-18  
**测试文件**: test_bili_service_unit.py  
**结果**: ✅ 全部通过

```
测试总结:
  运行测试: 29
  成功: 29
  失败: 0
  错误: 0
  
通过率: 100%
```

---

## 🎓 扩展测试

### 添加新测试

1. 在相应的测试类中添加测试方法
2. 方法名必须以 `test_` 开头
3. 使用 `self.assert*` 进行断言

示例：

```python
def test_new_feature(self):
    """测试新功能"""
    service = BiliAudioService()
    result = service.new_method()
    self.assertEqual(result, expected_value)
```

### 性能测试

```python
import time

def test_performance(self):
    """测试性能"""
    service = BiliAudioService()
    
    start = time.time()
    service._parse_video_url('BV1xx411c7XD')
    elapsed = time.time() - start
    
    self.assertLess(elapsed, 0.1)  # 应在 100ms 内完成
```

---

## 📚 相关文档

- [BiliAudioService 集成指南](../docs/BiliAudioService集成指南.md)
- [服务模块说明](../backend/services/README_BILI.md)
- [交付文档](../docs/BiliAudioService交付文档.md)

---

**维护者**: AI Assistant  
**最后更新**: 2026-02-18  
**测试框架**: unittest  
**Python 版本**: 3.12+
