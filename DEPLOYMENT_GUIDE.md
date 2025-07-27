# 部署指南

## 问题解决

### 1. Vercel部署中的greenlet构建错误

**问题**: `ERROR: Failed building wheel for greenlet`

**解决方案**: 已更新 `backend/requirements.txt` 中的包版本：
- `greenlet==3.0.1` (从2.0.2升级)
- `SQLAlchemy==2.0.23` (从1.4.46升级)

### 2. 语音识别API部署

**问题**: 部署的网页无法正确调用语音识别API

**解决方案**: 
1. 使用Vercel部署后端API
2. 前端自动检测环境并调用正确的API
3. 提供本地模拟作为备用方案

## 部署步骤

### 方法1: 使用Vercel CLI (推荐)

#### Windows用户:
```bash
# 运行部署脚本
deploy.bat
```

#### Linux/Mac用户:
```bash
# 运行部署脚本
./deploy.sh
```

#### 手动部署:
```bash
# 1. 安装Vercel CLI
npm install -g vercel

# 2. 登录Vercel (首次使用)
vercel login

# 3. 部署到生产环境
vercel --prod
```

### 方法2: GitHub自动部署

1. 将代码推送到GitHub仓库
2. 在Vercel中连接GitHub仓库
3. Vercel会自动检测并部署

## 部署配置

### 文件结构
```
├── api/
│   └── index.py          # Vercel API入口
├── backend/
│   ├── app.py           # Flask应用
│   └── requirements.txt  # Python依赖
├── frontend/            # 前端文件
├── vercel.json          # Vercel配置
└── deploy.sh/deploy.bat # 部署脚本
```

### 环境变量配置

在Vercel项目设置中添加以下环境变量：
- `DOUBAO_API_KEY`: 豆包AI API密钥
- `BAIDU_ASR_API_KEY`: 百度语音识别API密钥
- `BAIDU_ASR_SECRET_KEY`: 百度语音识别密钥

## API端点

部署后的API地址: `https://forbites.vercel.app/api`

主要端点:
- `GET /api/health` - 健康检查
- `POST /api/pantry/voice_recognize` - 语音识别
- `POST /api/recipe/filters` - 保存筛选条件
- `GET /api/recipe/filters` - 获取筛选条件

## 故障排除

### 1. 构建失败
- 检查 `requirements.txt` 中的包版本兼容性
- 确保Python版本为3.9+

### 2. API调用失败
- 检查环境变量是否正确设置
- 查看Vercel函数日志
- 前端会自动回退到本地模拟

### 3. 语音识别问题
- 确保百度语音识别API密钥有效
- 检查音频格式是否正确
- 前端提供本地模拟作为备用

## 测试

### 测试API连接
```bash
curl https://forbites.vercel.app/api/health
```

### 测试语音识别
访问: `https://forbites.vercel.app/frontend/ingredients.html`

## 支持的环境

- ✅ Vercel部署 (推荐)
- ✅ 本地开发
- ✅ 静态文件部署 (带本地模拟)

## 联系支持

如遇到问题，请检查：
1. Vercel部署日志
2. 浏览器控制台错误
3. 网络连接状态 