# Videos to Text - React Frontend

React + Vite 前端应用

## 技术栈

- React 18
- Vite (构建工具)
- Axios (HTTP 客户端)

## 安装依赖

```bash
npm install
```

## 开发

```bash
npm run dev
```

访问 http://localhost:3000

## 构建

```bash
npm run build
```

构建输出在 `dist/` 目录

## 环境变量

创建 `.env.local` 文件配置 API 地址：

```
VITE_API_URL=http://localhost:5000/api
```

## 项目结构

```
src/
├── components/          # React 组件
│   ├── UploadPage.jsx   # 上传页面
│   └── ResultPage.jsx   # 结果页面
├── utils/               # 工具函数
│   └── api.js           # API 调用
├── App.jsx              # 主应用组件
├── App.css              # 应用样式
├── main.jsx             # 入口文件
└── index.css            # 全局样式
```
