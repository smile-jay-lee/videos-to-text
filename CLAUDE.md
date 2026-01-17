# AI工作规范

## 基本规则

### 1. 文件组织
- 测试文件 → `tests/` 目录
- 文档文件 → `docs/` 目录

### 2. 代码修改
- 修改前先 `read_file` 查看接口
- 使用 `multi_replace_string_in_file` 批量修改
- oldString 包含3-5行上下文

### 3. Git操作
- ❌ 禁止使用 GitLens 工具
- ✅ 必须使用命令行: `git add`, `git commit`, `git push`
- 提交信息要清晰描述改动

### 4. 终端命令
- PowerShell使用 `;` 连接命令（不用 `&&`）
- 后台进程设置 `isBackground=true`
- 修改Python代码后必须清理 `__pycache__` 并重启

### 5. 响应方式
- 简单操作: 1-3句话
- 避免冗余开场白
- 文件引用使用Markdown链接格式

## 本项目特定

### Whisper配置
- 模型位置: `D:\project\videos to text\models\`
- 推荐: small(⭐⭐⭐) / medium(⭐⭐⭐⭐)

### 防幻觉参数（必须）
```python
'condition_on_previous_text': False,
'compression_ratio_threshold': 2.4,
'logprob_threshold': -1.0,
'no_speech_threshold': 0.6,
```

### 中文文件名
- 使用 `get_secure_filename()`
- 保留Unicode: `\u4e00-\u9fff`
