# Binance 空投信息平台部署指南

## 🚀 部署方式

### 1. Heroku 部署（推荐）

#### 步骤 1: 准备文件
确保以下文件存在：
- `realtime_platform.py` - 主应用文件
- `requirements.txt` - Python 依赖
- `Procfile` - Heroku 启动配置
- `runtime.txt` - Python 版本

#### 步骤 2: 创建 Heroku 应用
```bash
# 安装 Heroku CLI
# 登录 Heroku
heroku login

# 创建应用
heroku create your-app-name

# 设置环境变量（如果需要代理）
heroku config:set TWS_PROXY="your-proxy-url"

# 部署
git add .
git commit -m "Deploy Binance airdrop platform"
git push heroku main
```

#### 步骤 3: 启动应用
```bash
heroku ps:scale web=1
heroku open
```

### 2. VPS 部署

#### 使用 Gunicorn + Nginx

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
gunicorn --bind 0.0.0.0:8000 realtime_platform:app

# 使用 systemd 管理服务
sudo nano /etc/systemd/system/airdrop-platform.service
```

服务配置文件：
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

### 3. Docker 部署

#### 创建 Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "realtime_platform:app"]
```

#### 构建和运行
```bash
docker build -t binance-airdrop-platform .
docker run -p 8000:8000 binance-airdrop-platform
```

## ⚙️ 配置说明

### 环境变量
- `TWS_PROXY`: 代理地址（可选）
- `PORT`: 端口号（Heroku 自动设置）
- `UPDATE_INTERVAL`: 更新间隔（秒）

### 数据库
- 使用 SQLite 数据库存储推文
- 自动创建数据库文件 `airdrop_data.db`
- 支持数据持久化

## 🔧 功能特性

### 实时更新机制
- **自动更新**: 每5分钟自动爬取新推文
- **后台运行**: 使用独立线程，不影响 Web 服务
- **智能筛选**: 自动识别空投相关推文
- **数据存储**: SQLite 数据库持久化存储

### API 接口
- `GET /` - 主页
- `GET /api/airdrop-tweets` - 获取空投推文
- `GET /api/force-update` - 手动触发更新

### 前端功能
- 响应式设计
- 实时数据展示
- 自动刷新（30秒）
- 统计信息展示

## 📊 监控和维护

### 日志查看
```bash
# Heroku
heroku logs --tail

# VPS
journalctl -u airdrop-platform -f
```

### 手动更新
访问 `/api/force-update` 端点手动触发更新

### 数据库管理
```bash
# 查看数据库
sqlite3 airdrop_data.db
.tables
SELECT COUNT(*) FROM airdrop_tweets;
```

## 🚨 注意事项

1. **代理配置**: 如果在中国大陆，建议配置代理
2. **速率限制**: Twitter API 有速率限制，建议不要过于频繁更新
3. **数据备份**: 定期备份数据库文件
4. **监控**: 建议设置监控确保服务正常运行

## 🔄 更新流程

1. 修改代码
2. 测试本地运行
3. 提交到 Git
4. 部署到生产环境
5. 验证功能正常

## 📞 技术支持

如有问题，请检查：
1. 日志文件
2. 数据库连接
3. 网络连接
4. 依赖安装
