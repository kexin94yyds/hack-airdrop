#!/usr/bin/env python3
"""
简化版 Binance 空投信息平台
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime
from flask import Flask, render_template, jsonify
import threading

# 导入 twscrape
from twscrape import API

app = Flask(__name__)

# 配置
PROXY_URL = "http://127.0.0.1:7897"
DB_PATH = "airdrop_data.db"

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

class SimpleAirdropScraper:
    def __init__(self):
        self.api = API(proxy=PROXY_URL)
        self.db_path = DB_PATH
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
            except sqlite3.IntegrityError:
                pass
        
        conn.commit()
        conn.close()
    
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

# 全局爬虫实例
scraper = SimpleAirdropScraper()

@app.route('/')
def index():
    """主页"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Binance 空投信息平台</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="#">
                    <i class="fab fa-bitcoin"></i> Binance 空投信息平台
                </a>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-gift text-success"></i> 空投相关信息</h5>
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
                        renderTweets(data.data);
                    }
                } catch (error) {
                    console.error('加载推文失败:', error);
                }
            }
            
            function renderTweets(tweets) {
                const container = document.getElementById('tweets-container');
                
                if (tweets.length === 0) {
                    container.innerHTML = '<div class="text-center py-5"><h5 class="text-muted">暂无空投相关信息</h5></div>';
                    return;
                }
                
                const tweetsHTML = tweets.map(tweet => `
                    <div class="card mb-3">
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
                                            `<span class="badge bg-success me-1">${keyword}</span>`
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
                                    <i class="fas fa-heart text-danger"></i> ${tweet.likes} 
                                    <i class="fas fa-retweet text-success ms-2"></i> ${tweet.retweets}
                                    <i class="fas fa-reply text-info ms-2"></i> ${tweet.replies}
                                </small>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                container.innerHTML = tweetsHTML;
            }
            
            // 页面加载时获取数据
            loadTweets();
            
            // 每5分钟自动刷新
            setInterval(loadTweets, 300000);
        </script>
    </body>
    </html>
    """

@app.route('/api/airdrop-tweets')
def get_airdrop_tweets():
    """获取空投推文 API"""
    limit = request.args.get('limit', 20, type=int)
    tweets = scraper.get_airdrop_tweets(limit)
    return jsonify({
        'success': True,
        'data': tweets,
        'timestamp': datetime.now().isoformat()
    })

def background_updater():
    """后台更新任务"""
    while True:
        try:
            print(f"[{datetime.now()}] 开始更新 Binance 推文...")
            
            # 在新的事件循环中运行异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tweets = loop.run_until_complete(scraper.scrape_binance_tweets(50))
            loop.close()
            
            if tweets:
                scraper.save_tweets_to_db(tweets)
                airdrop_tweets = scraper.get_airdrop_tweets(10)
                print(f"[{datetime.now()}] 更新完成: {len(tweets)} 条推文, {len(airdrop_tweets)} 条空投相关")
            else:
                print(f"[{datetime.now()}] 更新失败: 未获取到推文")
                
        except Exception as e:
            print(f"后台更新出错: {e}")
        
        time.sleep(300)  # 5分钟更新一次

if __name__ == '__main__':
    # 启动后台更新线程
    update_thread = threading.Thread(target=background_updater, daemon=True)
    update_thread.start()
    
    print("🚀 Binance 空投信息平台启动中...")
    print("📊 功能特性:")
    print("   • 实时爬取 @binance 推文")
    print("   • 智能筛选空投相关信息")
    print("   • Web 界面展示")
    print("   • 自动更新机制")
    print()
    print("🌐 访问地址: http://localhost:5000")
    print("⏰ 更新间隔: 5分钟")
    print("🔄 按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # 启动 Flask 应用
    app.run(debug=True, host='0.0.0.0', port=5000)
