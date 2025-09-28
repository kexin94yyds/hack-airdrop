# 🚀 Binance 空投信息平台部署指南

## 方式一：Heroku 部署（推荐）

### 步骤 1: 安装 Heroku CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku

# 或者下载安装包
# https://devcenter.heroku.com/articles/heroku-cli
```

### 步骤 2: 登录 Heroku
```bash
heroku login
```

### 步骤 3: 创建应用
```bash
cd /Users/apple/twiter/twscrape
heroku create your-app-name
```

### 步骤 4: 部署
```bash
git push heroku main
```

### 步骤 5: 启动应用
```bash
heroku ps:scale web=1
heroku open
```

## 方式二：Vercel 部署（更简单）

### 步骤 1: 安装 Vercel CLI
```bash
npm i -g vercel
```

### 步骤 2: 创建 vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "realtime_platform.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "realtime_platform.py"
    }
  ]
}
```

### 步骤 3: 部署
```bash
vercel --prod
```

## 方式三：Railway 部署（最简单）

### 步骤 1: 访问 Railway
访问 https://railway.app

### 步骤 2: 连接 GitHub
- 登录 Railway
- 点击 "New Project"
- 选择 "Deploy from GitHub repo"
- 选择你的仓库

### 步骤 3: 自动部署
Railway 会自动检测到 Python 项目并部署

## 方式四：本地 VPS 部署

### 使用 Gunicorn
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
gunicorn --bind 0.0.0.0:8000 realtime_platform:app
```

### 使用 systemd 管理
```bash
sudo nano /etc/systemd/system/airdrop-platform.service
```

服务配置：
```ini
[Unit]
Description=Binance Airdrop Platform
After=network.target

[Service]
Type=exec
User=your-user
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/gunicorn --bind 0.0.0.0:8000 realtime_platform:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable airdrop-platform
sudo systemctl start airdrop-platform
```

## 🔧 环境变量配置

### Heroku
```bash
heroku config:set TWS_PROXY="your-proxy-url"
```

### Railway/Vercel
在项目设置中添加环境变量：
- `TWS_PROXY`: 代理地址（可选）

## 📊 功能特性

✅ **实时更新**: 每5分钟自动爬取新推文
✅ **智能筛选**: 自动识别空投相关推文  
✅ **Web界面**: 美观的响应式界面
✅ **API接口**: RESTful API 支持
✅ **数据存储**: SQLite 数据库持久化
✅ **生产就绪**: 支持 Gunicorn 部署

## 🌐 访问地址

部署成功后，你将获得：
- **Web界面**: https://your-app-name.herokuapp.com
- **API接口**: https://your-app-name.herokuapp.com/api/airdrop-tweets
- **手动更新**: https://your-app-name.herokuapp.com/api/force-update

## 📱 使用说明

1. **访问主页**: 查看空投信息统计
2. **浏览推文**: 查看筛选出的空投相关推文
3. **搜索功能**: 使用关键词搜索特定内容
4. **自动刷新**: 页面每30秒自动刷新数据
5. **手动更新**: 点击刷新按钮或访问API强制更新

## 🚨 注意事项

1. **代理配置**: 如果在中国大陆，建议配置代理
2. **速率限制**: Twitter API 有速率限制，建议不要过于频繁更新
3. **数据备份**: 定期备份数据库文件
4. **监控**: 建议设置监控确保服务正常运行

## 🔄 更新流程

1. 修改代码
2. 提交到 Git
3. 推送到部署平台
4. 自动部署完成

## 📞 技术支持

如有问题，请检查：
1. 日志文件
2. 数据库连接
3. 网络连接
4. 依赖安装
