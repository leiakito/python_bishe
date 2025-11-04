# 安装与启动指南

## 环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0 或 yarn >= 1.22.0

## 安装步骤

### 1. 安装依赖

```bash
cd front
npm install
```

或使用 yarn:

```bash
yarn install
```

### 2. 配置环境变量

项目已包含开发和生产环境配置文件:
- `.env.development` - 开发环境配置
- `.env.production` - 生产环境配置

开发环境默认配置:
```
VITE_API_BASE_URL=http://localhost:8000
```

如需修改后端API地址，请编辑对应的环境配置文件。

### 3. 启动开发服务器

```bash
npm run dev
```

项目将在 `http://localhost:3000` 启动，并自动打开浏览器。

### 4. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录。

### 5. 预览生产构建

```bash
npm run preview
```

## 项目结构

```
front/
├── public/              # 静态资源
├── src/
│   ├── api/            # API接口封装
│   │   ├── user.js     # 用户相关接口
│   │   ├── house.js    # 房源相关接口
│   │   ├── favorite.js # 收藏和提醒接口
│   │   └── analysis.js # 数据分析接口
│   ├── assets/         # 资源文件
│   ├── components/     # 公共组件
│   │   └── HouseCard.vue
│   ├── router/         # 路由配置
│   │   └── index.js
│   ├── stores/         # Pinia状态管理
│   │   ├── user.js     # 用户状态
│   │   └── house.js    # 房源状态
│   ├── views/          # 页面组件
│   │   ├── auth/       # 认证页面
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   ├── house/      # 房源页面
│   │   │   ├── List.vue
│   │   │   └── Detail.vue
│   │   ├── user/       # 用户中心页面
│   │   │   ├── Profile.vue
│   │   │   ├── Favorites.vue
│   │   │   ├── PriceAlerts.vue
│   │   │   └── MyHouses.vue
│   │   ├── Home.vue    # 首页
│   │   ├── Map.vue     # 地图找房
│   │   ├── Analysis.vue # 数据分析
│   │   ├── Layout.vue  # 布局组件
│   │   └── NotFound.vue # 404页面
│   ├── utils/          # 工具函数
│   │   ├── request.js  # Axios封装
│   │   ├── auth.js     # 认证工具
│   │   └── index.js    # 通用工具
│   ├── styles/         # 全局样式
│   │   └── index.scss
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
├── index.html          # HTML模板
├── vite.config.js      # Vite配置
├── package.json        # 项目配置
└── README.md           # 项目说明
```

## 功能模块

### 用户认证
- ✅ 用户注册
- ✅ 用户登录
- ✅ JWT Token认证
- ✅ 个人信息管理
- ✅ 密码修改

### 房源管理
- ✅ 房源列表展示
- ✅ 高级搜索与筛选
- ✅ 房源详情查看
- ✅ 房源发布（经纪人）
- ✅ 房源编辑（经纪人）
- ✅ 房源删除（经纪人）

### 收藏与提醒
- ✅ 房源收藏
- ✅ 收藏列表管理
- ✅ 价格提醒设置
- ✅ 提醒状态跟踪

### 数据分析
- ✅ 价格趋势分析
- ✅ 区域对比分析
- ✅ 户型分布统计
- ✅ 价格区间分布
- ✅ 房价预测

### 地图功能
- ✅ 地图找房
- ✅ 房源标记
- ✅ 地图筛选

## 技术特点

### 现代化技术栈
- Vue 3 Composition API
- Vite 5 快速构建
- Element Plus UI组件库
- Pinia 状态管理
- Vue Router 4 路由管理

### 优秀的开发体验
- 热模块替换(HMR)
- TypeScript支持（可选）
- ESLint代码检查
- 组件化开发

### 性能优化
- 路由懒加载
- 组件按需加载
- 图片懒加载
- 代码分割

### 响应式设计
- 移动端适配
- 平板适配
- 桌面端适配

## API对接

所有API请求通过Vite代理转发到后端服务器:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## 常见问题

### 1. 安装依赖失败

尝试清除缓存后重新安装:
```bash
rm -rf node_modules package-lock.json
npm install
```

### 2. 启动失败

检查端口3000是否被占用，可以在 `vite.config.js` 中修改端口:
```javascript
server: {
  port: 3001
}
```

### 3. API请求失败

确保后端服务已启动在 `http://localhost:8000`，并检查CORS配置。

### 4. 地图不显示

检查网络连接，确保可以访问OpenStreetMap服务。

## 部署

### Nginx部署

1. 构建生产版本:
```bash
npm run build
```

2. 将 `dist` 目录上传到服务器

3. Nginx配置示例:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend-server:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 开发规范

### 组件命名
- 使用PascalCase命名组件文件
- 组件名至少两个单词

### 代码风格
- 使用ESLint检查代码
- 遵循Vue官方风格指南
- 使用Prettier格式化代码

### Git提交
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

## 许可证

MIT License

