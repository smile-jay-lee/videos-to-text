# Frontend - 视频转文字前端

## 目录结构

```
frontend/
├── templates/        # HTML模板
│   ├── base.html     # 基础模板
│   ├── index.html    # 首页
│   ├── upload.html   # 上传页面
│   └── result.html   # 结果展示页面
└── static/           # 静态资源
    ├── css/          # 样式文件
    │   └── style.css
    ├── js/           # JavaScript文件
    └── uploads/      # 文件上传目录
```

## 说明

前端使用 Flask 模板引擎渲染，静态文件由 Flask 提供服务。

所有页面继承自 `base.html` 基础模板，保持统一的样式和结构。
