#!/usr/bin/env python3
"""
实时更新版 Binance 空投信息平台
支持真正的实时爬取和更新
"""

import asyncio
import json
import sqlite3
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import os

# 导入 twscrape
from twscrape import API

app = Flask(__name__)

# 配置
PROXY_URL = "http://127.0.0.1:7897"  # 可选，如果不需要代理可以设为 None
DB_PATH = "airdrop_data.db"
UPDATE_INTERVAL = 300  # 5分钟更新一次

# 空投相关关键词
AIRDROP_KEYWORDS = [
    'airdrop', 'airdrops', 'air drop', 'air drops',
    'free tokens', 'free crypto', 'claim', 'claiming',
    'distribution', 'reward', 'rewards', 'bonus',
    'giveaway', 'giveaways', 'contest', 'competition',
    'launch', 'launching', 'new token', 'new coin',
    'listing', 'new listing', 'trading', 'trade',
    'stake', 'staking', 'farm', 'farming',
    'liquidity', 'pool', 'mining', 'yield'
]

class RealtimeAirdropScraper:
    def __init__(self):
        self.api = API(proxy=PROXY_URL) if PROXY_URL else API()
        self.db_path = DB_PATH
        self.last_update = None
        self.init_database()
        
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS airdrop_tweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tweet_id TEXT UNIQUE,
                content TEXT,
                url TEXT,
                date TEXT,
                likes INTEGER,
                retweets INTEGER,
                replies INTEGER,
                is_airdrop BOOLEAN,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_airdrop_related(self, content: str):
        """判断推文是否与空投相关"""
        content_lower = content.lower()
        found_keywords = []
        
        for keyword in AIRDROP_KEYWORDS:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords
    
    async def scrape_binance_tweets(self, limit: int = 50):
        """爬取 Binance 推文"""
        try:
            tweets = []
            async for tweet in self.api.search("from:binance", limit=limit):
                tweet_data = {
                    'id': tweet.id,
                    'content': tweet.rawContent,
                    'url': tweet.url,
                    'date': tweet.date.isoformat(),
                    'likes': tweet.likeCount,
                    'retweets': tweet.retweetCount,
                    'replies': tweet.replyCount,
                    'user': {
                        'username': tweet.user.username,
                        'displayname': tweet.user.displayname,
                        'followers': tweet.user.followersCount
                    }
                }
                tweets.append(tweet_data)
            
            return tweets
        except Exception as e:
            print(f"爬取推文时出错: {e}")
            return []
    
    def save_tweets_to_db(self, tweets):
        """保存推文到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_count = 0
        for tweet in tweets:
            is_airdrop, keywords = self.is_airdrop_related(tweet['content'])
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO airdrop_tweets 
                    (tweet_id, content, url, date, likes, retweets, replies, is_airdrop, keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tweet['id'],
                    tweet['content'],
                    tweet['url'],
                    tweet['date'],
                    tweet['likes'],
                    tweet['retweets'],
                    tweet['replies'],
                    is_airdrop,
                    ','.join(keywords)
                ))
                new_count += 1
            except sqlite3.IntegrityError:
                # 推文已存在，跳过
                pass
        
        conn.commit()
        conn.close()
        return new_count
    
    def get_airdrop_tweets(self, limit: int = 20):
        """从数据库获取空投相关推文"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tweet_id, content, url, date, likes, retweets, replies, keywords
            FROM airdrop_tweets 
            WHERE is_airdrop = 1 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        tweets = []
        for row in cursor.fetchall():
            tweets.append({
                'id': row[0],
                'content': row[1],
                'url': row[2],
                'date': row[3],
                'likes': row[4],
                'retweets': row[5],
                'replies': row[6],
                'keywords': row[7].split(',') if row[7] else []
            })
        
        conn.close()
        return tweets
    
    def get_stats(self):
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总推文数
        cursor.execute('SELECT COUNT(*) FROM airdrop_tweets')
        total_tweets = cursor.fetchone()[0]
        
        # 空投推文数
        cursor.execute('SELECT COUNT(*) FROM airdrop_tweets WHERE is_airdrop = 1')
        airdrop_tweets = cursor.fetchone()[0]
        
        # 今日新增
        today = datetime.now().date()
        cursor.execute('SELECT COUNT(*) FROM airdrop_tweets WHERE DATE(created_at) = ?', (today,))
        today_tweets = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_tweets': total_tweets,
            'airdrop_tweets': airdrop_tweets,
            'today_tweets': today_tweets,
            'airdrop_rate': round((airdrop_tweets / total_tweets * 100), 2) if total_tweets > 0 else 0,
            'last_update': self.last_update
        }
    
    async def update_tweets(self):
        """更新推文数据"""
        print(f"[{datetime.now()}] 开始更新 Binance 推文...")
        
        tweets = await self.scrape_binance_tweets(100)
        if tweets:
            new_count = self.save_tweets_to_db(tweets)
            self.last_update = datetime.now()
            print(f"[{datetime.now()}] 更新完成: {len(tweets)} 条推文, 新增 {new_count} 条")
        else:
            print(f"[{datetime.now()}] 更新失败: 未获取到推文")

# 全局爬虫实例
scraper = RealtimeAirdropScraper()

@app.route('/')
def index():
    """主页"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Binance 空投信息平台 - 实时版</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .tweet-card { border-left: 4px solid #28a745; margin-bottom: 1rem; transition: all 0.3s ease; }
            .tweet-card:hover { border-left-color: #20c997; background-color: #f8f9fa; }
            .keyword-badge { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 12px; margin: 0.125rem; display: inline-block; }
            .status-indicator { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 0.5rem; }
            .status-online { background-color: #28a745; animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="#">
                    <i class="fab fa-bitcoin"></i> Binance 空投信息平台
                </a>
                <div class="navbar-nav ms-auto">
                    <span class="navbar-text">
                        <span class="status-indicator status-online"></span>
                        <span id="last-update">实时更新中...</span>
                    </span>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <h4 class="card-title" id="total-tweets">-</h4>
                            <p class="card-text">总推文数</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h4 class="card-title" id="airdrop-tweets">-</h4>
                            <p class="card-text">空投推文</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body">
                            <h4 class="card-title" id="today-tweets">-</h4>
                            <p class="card-text">今日新增</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body">
                            <h4 class="card-title" id="airdrop-rate">-</h4>
                            <p class="card-text">空投比例</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5><i class="fas fa-gift text-success"></i> 空投相关信息</h5>
                            <button class="btn btn-sm btn-outline-primary" onclick="loadTweets()">
                                <i class="fas fa-sync-alt"></i> 刷新
                            </button>
                        </div>
                        <div class="card-body">
                            <div id="tweets-container">
                                <div class="text-center py-5">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">加载中...</span>
                                    </div>
                                    <p class="mt-3 text-muted">正在加载空投信息...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            async function loadTweets() {
                try {
                    const response = await fetch('/api/airdrop-tweets');
                    const data = await response.json();
                    
                    if (data.success) {
                        updateStats(data.stats);
                        renderTweets(data.data);
                        updateLastUpdateTime(data.stats.last_update);
                    }
                } catch (error) {
                    console.error('加载推文失败:', error);
                }
            }
            
            function updateStats(stats) {
                document.getElementById('total-tweets').textContent = stats.total_tweets.toLocaleString();
                document.getElementById('airdrop-tweets').textContent = stats.airdrop_tweets.toLocaleString();
                document.getElementById('today-tweets').textContent = stats.today_tweets.toLocaleString();
                document.getElementById('airdrop-rate').textContent = stats.airdrop_rate + '%';
            }
            
            function updateLastUpdateTime(timestamp) {
                if (timestamp) {
                    const updateTime = new Date(timestamp);
                    const timeString = updateTime.toLocaleTimeString('zh-CN');
                    document.getElementById('last-update').textContent = `最后更新: ${timeString}`;
                }
            }
            
            function renderTweets(tweets) {
                const container = document.getElementById('tweets-container');
                
                if (tweets.length === 0) {
                    container.innerHTML = '<div class="text-center py-5"><h5 class="text-muted">暂无空投相关信息</h5></div>';
                    return;
                }
                
                const tweetsHTML = tweets.map(tweet => `
                    <div class="card tweet-card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div class="flex-grow-1">
                                    <p class="card-text">${tweet.content}</p>
                                    <div class="text-muted small">
                                        <i class="fab fa-twitter text-primary"></i> 
                                        <strong>@binance</strong> • ${new Date(tweet.date).toLocaleString('zh-CN')}
                                    </div>
                                    <div class="mt-2">
                                        ${tweet.keywords.map(keyword => 
                                            `<span class="keyword-badge">${keyword}</span>`
                                        ).join('')}
                                    </div>
                                </div>
                                <div class="ms-3">
                                    <a href="${tweet.url}" target="_blank" class="btn btn-primary btn-sm">
                                        <i class="fab fa-twitter"></i> 查看
                                    </a>
                                </div>
                            </div>
                            <div class="mt-2">
                                <small class="text-muted">
                                    <i class="fas fa-heart text-danger"></i> ${tweet.likes.toLocaleString()} 
                                    <i class="fas fa-retweet text-success ms-2"></i> ${tweet.retweets.toLocaleString()}
                                    <i class="fas fa-reply text-info ms-2"></i> ${tweet.replies.toLocaleString()}
                                </small>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                container.innerHTML = tweetsHTML;
            }
            
            // 页面加载时获取数据
            loadTweets();
            
            // 每30秒自动刷新
            setInterval(loadTweets, 30000);
        </script>
    </body>
    </html>
    """

@app.route('/api/airdrop-tweets')
def get_airdrop_tweets():
    """获取空投推文 API"""
    limit = request.args.get('limit', 20, type=int)
    tweets = scraper.get_airdrop_tweets(limit)
    stats = scraper.get_stats()
    
    return jsonify({
        'success': True,
        'data': tweets,
        'stats': stats
    })

@app.route('/api/force-update')
def force_update():
    """手动触发更新"""
    def run_update():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(scraper.update_tweets())
        loop.close()
    
    # 在后台线程中运行更新
    thread = threading.Thread(target=run_update)
    thread.start()
    
    return jsonify({
        'success': True,
        'message': '更新已开始，请稍后刷新页面查看结果'
    })

def background_updater():
    """后台更新任务"""
    while True:
        try:
            # 在新的事件循环中运行异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(scraper.update_tweets())
            loop.close()
        except Exception as e:
            print(f"后台更新出错: {e}")
        
        time.sleep(UPDATE_INTERVAL)

if __name__ == '__main__':
    # 启动后台更新线程
    update_thread = threading.Thread(target=background_updater, daemon=True)
    update_thread.start()
    
    print("🚀 Binance 空投信息平台启动中...")
    print("📊 功能特性:")
    print("   • 实时爬取 @binance 推文")
    print("   • 智能筛选空投相关信息")
    print("   • Web 界面展示")
    print("   • 自动更新机制 (每5分钟)")
    print("   • 数据库存储")
    print()
    print("🌐 访问地址: http://localhost:9000")
    print("⏰ 更新间隔: 5分钟")
    print("🔄 按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # 启动 Flask 应用
    app.run(debug=False, host='0.0.0.0', port=9000)
