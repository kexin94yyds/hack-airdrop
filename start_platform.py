#!/usr/bin/env python3
"""
启动 Binance 空投信息平台
"""

import subprocess
import sys
import os

def install_dependencies():
    """安装平台依赖"""
    print("📦 安装平台依赖...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "Flask==2.3.3",
            "Flask-SocketIO==5.3.6", 
            "python-socketio==5.8.0",
            "eventlet==0.33.3"
        ])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def start_platform():
    """启动平台"""
    print("🚀 启动 Binance 空投信息平台...")
    print("📊 功能特性:")
    print("   • 实时爬取 @binance 推文")
    print("   • 智能筛选空投相关信息")
    print("   • Web 界面实时展示")
    print("   • 自动更新机制")
    print("   • 搜索和排序功能")
    print()
    print("🌐 访问地址: http://localhost:5000")
    print("⏰ 更新间隔: 5分钟")
    print("🔄 按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        # 启动平台
        os.system("python airdrop_platform.py")
    except KeyboardInterrupt:
        print("\n👋 平台已停止")

if __name__ == "__main__":
    if install_dependencies():
        start_platform()
    else:
        print("❌ 无法启动平台，请检查依赖安装")
        sys.exit(1)
