#!/usr/bin/env python3
"""
Binance 空投信息实时更新平台
实时爬取 @binance 推文，筛选空投相关信息并展示
"""

import asyncio
import json
import os
import re
import sqlite3
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import httpx
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading

# 导入 twscrape
from twscrape import API
from twscrape.logger import set_log_level

app = Flask(__name__)
app.config['SECRET_KEY'] = 'binance_airdrop_platform_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# 配置
PROXY_URL = "http://127.0.0.1:7897"
UPDATE_INTERVAL = 300  # 5分钟更新一次
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

class BinanceAirdropScraper:
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
    
    def is_airdrop_related(self, content: str) -> tuple[bool, List[str]]:
        """判断推文是否与空投相关"""
        content_lower = content.lower()
        found_keywords = []
        
        for keyword in AIRDROP_KEYWORDS:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords
    
    async def scrape_binance_tweets(self, limit: int = 50) -> List[Dict]:
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
    
    def save_tweets_to_db(self, tweets: List[Dict]):
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
                # 推文已存在，跳过
                pass
        
        conn.commit()
        conn.close()
    
    def get_airdrop_tweets(self, limit: int = 20) -> List[Dict]:
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
    
    async def update_tweets(self):
        """更新推文数据"""
        print(f"[{datetime.now()}] 开始更新 Binance 推文...")
        
        tweets = await self.scrape_binance_tweets(100)
        if tweets:
            self.save_tweets_to_db(tweets)
            airdrop_tweets = self.get_airdrop_tweets(10)
            
            # 通过 WebSocket 发送更新
            socketio.emit('tweets_update', {
                'timestamp': datetime.now().isoformat(),
                'total_tweets': len(tweets),
                'airdrop_tweets': airdrop_tweets
            })
            
            print(f"[{datetime.now()}] 更新完成: {len(tweets)} 条推文, {len(airdrop_tweets)} 条空投相关")
        else:
            print(f"[{datetime.now()}] 更新失败: 未获取到推文")

# 全局爬虫实例
scraper = BinanceAirdropScraper()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

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

@app.route('/api/stats')
def get_stats():
    """获取统计信息 API"""
    conn = sqlite3.connect(DB_PATH)
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
    
    return jsonify({
        'success': True,
        'data': {
            'total_tweets': total_tweets,
            'airdrop_tweets': airdrop_tweets,
            'today_tweets': today_tweets,
            'airdrop_rate': round((airdrop_tweets / total_tweets * 100), 2) if total_tweets > 0 else 0
        }
    })

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    print('客户端已连接')
    emit('connected', {'message': '连接成功'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    print('客户端已断开连接')

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
    print(f"📊 更新间隔: {UPDATE_INTERVAL} 秒")
    print(f"🌐 访问地址: http://localhost:5000")
    
    # 启动 Flask 应用
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
