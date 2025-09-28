# 🚀 Hack Airdrop - Binance 空投信息实时监控平台

一个基于 `twscrape` 的实时空投信息监控平台，专门监控 Binance 官方推文中的空投活动。

## ✨ 功能特性

- 🔄 **实时监控**: 每5分钟自动爬取 @binance 最新推文
- 🎯 **智能筛选**: 自动识别空投相关推文
- 🌐 **Web界面**: 现代化的响应式Web界面
- 📊 **数据统计**: 实时显示空投推文统计信息
- 🔍 **搜索功能**: 支持关键词搜索
- 💾 **数据持久化**: SQLite数据库存储历史数据
- 🚀 **一键部署**: 支持多种部署平台

## 🛠️ 技术栈

- **后端**: Python Flask + twscrape
- **前端**: HTML5 + CSS3 + JavaScript
- **数据库**: SQLite
- **部署**: Vercel / Railway / Heroku

## 📦 安装与运行

### 1. 克隆项目
```bash
git clone https://github.com/kexin94yyds/hack-airdrop.git
cd hack-airdrop
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置账户
```bash
# 添加Twitter账户（需要cookies）
twscrape accounts add "username:password:email:email_password::cookies"
```

### 4. 运行平台
```bash
python realtime_platform.py
```

访问 http://localhost:9000 查看平台

## 🚀 部署

### Vercel 部署（推荐）
1. Fork 本仓库
2. 在 Vercel 中导入项目
3. 设置环境变量：
   - `TWS_PROXY`: 代理地址（如需要）
   - `UPDATE_INTERVAL`: 更新间隔（秒）
4. 部署完成

### Railway 部署
1. 连接 GitHub 仓库
2. 设置环境变量
3. 自动部署

### Heroku 部署
1. 创建 Heroku 应用
2. 连接 GitHub 仓库
3. 设置环境变量
4. 手动部署

## 📊 监控的空投关键词

- 空投, airdrop, airdrops
- #airdrop, #airdrops
- 空投活动, 领取空投
- HODLer Airdrop
- Launchpool
- 新币上线

## 🔧 环境变量

- `TWS_PROXY`: Twitter API代理地址
- `UPDATE_INTERVAL`: 更新间隔（默认300秒）
- `PORT`: 服务端口（默认9000）

## 📈 数据统计

平台会自动统计：
- 总推文数量
- 空投推文数量
- 空投比例
- 今日新增推文
- 最后更新时间

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## ⚠️ 免责声明

本项目仅供学习和研究使用，请遵守相关法律法规和平台服务条款。