# 🚀 快速部署指南

## 最简单方式：Railway 部署

### 步骤 1: 准备 GitHub 仓库
```bash
# 如果还没有 GitHub 仓库，先创建一个
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

### 步骤 2: 部署到 Railway
1. 访问 https://railway.app
2. 点击 "Start a New Project"
3. 选择 "Deploy from GitHub repo"
4. 连接你的 GitHub 账户
5. 选择你的仓库
6. Railway 会自动检测到 Python 项目并部署

### 步骤 3: 配置环境变量（可选）
如果需要代理，在 Railway 项目设置中添加：
- `TWS_PROXY`: 你的代理地址

## 部署文件说明

✅ **已准备的文件：**
- `realtime_platform.py` - 主应用文件（实时更新版本）
- `requirements.txt` - Python 依赖
- `Procfile` - Heroku 配置
- `railway.json` - Railway 配置
- `vercel.json` - Vercel 配置
- `runtime.txt` - Python 版本

## 功能特性

🎯 **实时更新机制：**
- 每5分钟自动爬取 @binance 推文
- 智能筛选空投相关信息
- SQLite 数据库持久化存储
- 后台线程运行，不影响 Web 服务

🌐 **Web 界面：**
- 响应式设计
- 实时数据展示
- 搜索和排序功能
- 统计信息展示

📡 **API 接口：**
- `GET /` - 主页
- `GET /api/airdrop-tweets` - 获取空投推文
- `GET /api/force-update` - 手动触发更新

## 部署后访问

部署成功后，你将获得一个 URL，例如：
- https://your-app-name.railway.app

访问这个 URL 即可使用平台！

## 其他部署方式

### Heroku 部署
```bash
# 安装 Heroku CLI
brew install heroku/brew/heroku

# 登录并创建应用
heroku login
heroku create your-app-name
git push heroku main
heroku ps:scale web=1
```

### Vercel 部署
```bash
# 安装 Vercel CLI
npm install -g vercel

# 部署
vercel --prod
```

## 监控和维护

- Railway 会自动重启崩溃的应用
- 查看日志：Railway 项目页面 → Deployments → 查看日志
- 手动更新：访问 `/api/force-update` 端点

## 注意事项

1. **免费额度**: Railway 有免费额度，足够个人使用
2. **代理配置**: 如果在中国大陆，建议配置代理
3. **数据持久化**: 使用 SQLite 数据库，数据会持久保存
4. **自动更新**: 平台会自动每5分钟更新一次数据
