#!/bin/bash

echo "🚀 Binance 空投信息平台一键部署脚本"
echo "=================================="

# 检查是否安装了必要的工具
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 未安装，请先安装 $1"
        return 1
    else
        echo "✅ $1 已安装"
        return 0
    fi
}

# 选择部署方式
echo ""
echo "请选择部署方式："
echo "1) Railway (推荐 - 最简单)"
echo "2) Heroku"
echo "3) Vercel"
echo "4) 本地 VPS"
echo ""
read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚂 部署到 Railway..."
        echo ""
        echo "步骤："
        echo "1. 访问 https://railway.app"
        echo "2. 点击 'New Project'"
        echo "3. 选择 'Deploy from GitHub repo'"
        echo "4. 连接你的 GitHub 仓库"
        echo "5. Railway 会自动检测并部署"
        echo ""
        echo "或者使用 Railway CLI："
        echo "npm install -g @railway/cli"
        echo "railway login"
        echo "railway init"
        echo "railway up"
        ;;
    2)
        echo ""
        echo "🟣 部署到 Heroku..."
        if check_command "heroku"; then
            echo ""
            read -p "请输入应用名称: " app_name
            echo "创建 Heroku 应用..."
            heroku create $app_name
            echo "部署到 Heroku..."
            git push heroku main
            echo "启动应用..."
            heroku ps:scale web=1
            echo "✅ 部署完成！访问: https://$app_name.herokuapp.com"
        else
            echo "请先安装 Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli"
        fi
        ;;
    3)
        echo ""
        echo "▲ 部署到 Vercel..."
        if check_command "vercel"; then
            echo "部署到 Vercel..."
            vercel --prod
            echo "✅ 部署完成！"
        else
            echo "请先安装 Vercel CLI: npm install -g vercel"
        fi
        ;;
    4)
        echo ""
        echo "🖥️  本地 VPS 部署..."
        echo ""
        echo "步骤："
        echo "1. 上传文件到 VPS"
        echo "2. 安装依赖: pip install -r requirements.txt"
        echo "3. 启动服务: gunicorn --bind 0.0.0.0:8000 realtime_platform:app"
        echo "4. 配置 Nginx 反向代理"
        echo ""
        echo "或者使用 systemd 管理服务"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 部署完成！"
echo ""
echo "📊 平台功能："
echo "• 实时爬取 @binance 推文"
echo "• 智能筛选空投相关信息"
echo "• Web 界面展示"
echo "• 自动更新机制 (每5分钟)"
echo "• API 接口支持"
echo ""
echo "📱 使用说明："
echo "• 访问主页查看空投信息"
echo "• 使用搜索功能查找特定内容"
echo "• 页面每30秒自动刷新"
echo "• 访问 /api/force-update 手动更新"
echo ""
echo "🔧 如需配置代理，请设置环境变量 TWS_PROXY"
