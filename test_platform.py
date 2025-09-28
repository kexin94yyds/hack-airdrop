#!/usr/bin/env python3
"""
测试版 Binance 空投信息平台
"""

from flask import Flask, jsonify
import json

app = Flask(__name__)

# 读取已有的 binance 推文数据
def load_binance_tweets():
    try:
        with open('binance_tweets.json', 'r', encoding='utf-8') as f:
            tweets = []
            for line in f:
                if line.strip():
                    tweet = json.loads(line.strip())
                    tweets.append(tweet)
            return tweets
    except FileNotFoundError:
        return []

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

def is_airdrop_related(content):
    """判断推文是否与空投相关"""
    content_lower = content.lower()
    found_keywords = []
    
    for keyword in AIRDROP_KEYWORDS:
        if keyword in content_lower:
            found_keywords.append(keyword)
    
    return len(found_keywords) > 0, found_keywords

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
        <style>
            .tweet-card { border-left: 4px solid #28a745; margin-bottom: 1rem; }
            .keyword-badge { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 12px; margin: 0.125rem; display: inline-block; }
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
                        <i class="fas fa-sync-alt"></i>
                        <span id="last-update">实时更新</span>
                    </span>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <h4 class="card-title" id="total-tweets">-</h4>
                            <p class="card-text">总推文数</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h4 class="card-title" id="airdrop-tweets">-</h4>
                            <p class="card-text">空投推文</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-info text-white">
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
                        updateStats(data.stats);
                        renderTweets(data.data);
                    }
                } catch (error) {
                    console.error('加载推文失败:', error);
                }
            }
            
            function updateStats(stats) {
                document.getElementById('total-tweets').textContent = stats.total_tweets;
                document.getElementById('airdrop-tweets').textContent = stats.airdrop_tweets;
                document.getElementById('airdrop-rate').textContent = stats.airdrop_rate + '%';
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
            
            // 每30秒自动刷新
            setInterval(loadTweets, 30000);
        </script>
    </body>
    </html>
    """

@app.route('/api/airdrop-tweets')
def get_airdrop_tweets():
    """获取空投推文 API"""
    tweets = load_binance_tweets()
    
    # 筛选空投相关推文
    airdrop_tweets = []
    for tweet in tweets:
        is_airdrop, keywords = is_airdrop_related(tweet['rawContent'])
        if is_airdrop:
            airdrop_tweets.append({
                'id': tweet['id'],
                'content': tweet['rawContent'],
                'url': tweet['url'],
                'date': tweet['date'],
                'likes': tweet['likeCount'],
                'retweets': tweet['retweetCount'],
                'replies': tweet['replyCount'],
                'keywords': keywords
            })
    
    # 计算统计信息
    total_tweets = len(tweets)
    airdrop_count = len(airdrop_tweets)
    airdrop_rate = round((airdrop_count / total_tweets * 100), 2) if total_tweets > 0 else 0
    
    return jsonify({
        'success': True,
        'data': airdrop_tweets[:20],  # 只返回前20条
        'stats': {
            'total_tweets': total_tweets,
            'airdrop_tweets': airdrop_count,
            'airdrop_rate': airdrop_rate
        }
    })

if __name__ == '__main__':
    print("🚀 Binance 空投信息平台启动中...")
    print("📊 功能特性:")
    print("   • 分析 @binance 推文")
    print("   • 智能筛选空投相关信息")
    print("   • Web 界面展示")
    print()
    print("🌐 访问地址: http://localhost:9000")
    print("🔄 按 Ctrl+C 停止服务")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=9000)
