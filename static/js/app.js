// Binance 空投信息平台前端 JavaScript

class AirdropPlatform {
    constructor() {
        this.socket = io();
        this.tweets = [];
        this.filteredTweets = [];
        this.init();
    }

    init() {
        this.setupSocketListeners();
        this.setupEventListeners();
        this.loadInitialData();
        this.startPeriodicUpdate();
    }

    setupSocketListeners() {
        // 连接成功
        this.socket.on('connect', () => {
            console.log('WebSocket 连接成功');
            this.updateConnectionStatus(true);
        });

        // 连接断开
        this.socket.on('disconnect', () => {
            console.log('WebSocket 连接断开');
            this.updateConnectionStatus(false);
        });

        // 接收推文更新
        this.socket.on('tweets_update', (data) => {
            console.log('收到推文更新:', data);
            this.handleTweetsUpdate(data);
        });

        // 连接确认
        this.socket.on('connected', (data) => {
            console.log('服务器确认连接:', data.message);
        });
    }

    setupEventListeners() {
        // 搜索功能
        document.getElementById('search-input').addEventListener('input', (e) => {
            this.filterTweets(e.target.value);
        });

        // 排序功能
        document.getElementById('sort-select').addEventListener('change', (e) => {
            this.sortTweets(e.target.value);
        });
    }

    async loadInitialData() {
        try {
            // 加载统计信息
            await this.loadStats();
            
            // 加载空投推文
            await this.loadAirdropTweets();
        } catch (error) {
            console.error('加载初始数据失败:', error);
            this.showError('加载数据失败，请刷新页面重试');
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (data.success) {
                this.updateStats(data.data);
            }
        } catch (error) {
            console.error('加载统计信息失败:', error);
        }
    }

    async loadAirdropTweets() {
        try {
            const response = await fetch('/api/airdrop-tweets?limit=50');
            const data = await response.json();
            
            if (data.success) {
                this.tweets = data.data;
                this.filteredTweets = [...this.tweets];
                this.renderTweets();
                this.updateTweetCount();
            }
        } catch (error) {
            console.error('加载空投推文失败:', error);
        }
    }

    handleTweetsUpdate(data) {
        // 更新最后更新时间
        this.updateLastUpdateTime(data.timestamp);
        
        // 重新加载数据
        this.loadInitialData();
        
        // 显示更新通知
        this.showUpdateNotification(data.total_tweets, data.airdrop_tweets.length);
    }

    updateStats(stats) {
        document.getElementById('total-tweets').textContent = stats.total_tweets.toLocaleString();
        document.getElementById('airdrop-tweets').textContent = stats.airdrop_tweets.toLocaleString();
        document.getElementById('today-tweets').textContent = stats.today_tweets.toLocaleString();
        document.getElementById('airdrop-rate').textContent = stats.airdrop_rate + '%';
    }

    updateConnectionStatus(isOnline) {
        const statusElement = document.getElementById('last-update');
        const syncIcon = document.getElementById('sync-icon');
        
        if (isOnline) {
            statusElement.innerHTML = '<span class="status-indicator status-online"></span>实时连接';
            syncIcon.classList.remove('sync-animation');
        } else {
            statusElement.innerHTML = '<span class="status-indicator status-offline"></span>连接断开';
            syncIcon.classList.add('sync-animation');
        }
    }

    updateLastUpdateTime(timestamp) {
        const lastUpdate = document.getElementById('last-update');
        const updateTime = new Date(timestamp);
        const timeString = updateTime.toLocaleTimeString('zh-CN');
        lastUpdate.innerHTML = `<span class="status-indicator status-online"></span>最后更新: ${timeString}`;
    }

    filterTweets(searchTerm) {
        if (!searchTerm.trim()) {
            this.filteredTweets = [...this.tweets];
        } else {
            const term = searchTerm.toLowerCase();
            this.filteredTweets = this.tweets.filter(tweet => 
                tweet.content.toLowerCase().includes(term) ||
                tweet.keywords.some(keyword => keyword.toLowerCase().includes(term))
            );
        }
        
        this.renderTweets();
        this.updateTweetCount();
    }

    sortTweets(sortType) {
        switch (sortType) {
            case 'newest':
                this.filteredTweets.sort((a, b) => new Date(b.date) - new Date(a.date));
                break;
            case 'popular':
                this.filteredTweets.sort((a, b) => (b.likes + b.retweets) - (a.likes + a.retweets));
                break;
            case 'recent':
                const yesterday = new Date();
                yesterday.setDate(yesterday.getDate() - 1);
                this.filteredTweets = this.filteredTweets.filter(tweet => 
                    new Date(tweet.date) > yesterday
                );
                break;
        }
        
        this.renderTweets();
    }

    renderTweets() {
        const container = document.getElementById('tweets-container');
        
        if (this.filteredTweets.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">没有找到相关推文</h5>
                    <p class="text-muted">尝试调整搜索条件或稍后再试</p>
                </div>
            `;
            return;
        }

        const tweetsHTML = this.filteredTweets.map(tweet => this.createTweetCard(tweet)).join('');
        container.innerHTML = tweetsHTML;
    }

    createTweetCard(tweet) {
        const date = new Date(tweet.date);
        const timeAgo = this.getTimeAgo(date);
        const keywords = tweet.keywords.map(keyword => 
            `<span class="keyword-badge">${keyword}</span>`
        ).join('');

        return `
            <div class="card tweet-card position-relative" onclick="app.showTweetModal('${tweet.id}')">
                <div class="airdrop-indicator">
                    <i class="fas fa-gift"></i> 空投
                </div>
                <div class="card-body">
                    <div class="tweet-content">${this.formatTweetContent(tweet.content)}</div>
                    <div class="tweet-meta">
                        <i class="fab fa-twitter text-primary"></i> 
                        <strong>@binance</strong> • ${timeAgo}
                    </div>
                    <div class="tweet-actions">
                        <span class="tweet-action">
                            <i class="fas fa-heart text-danger"></i>
                            <span>${tweet.likes.toLocaleString()}</span>
                        </span>
                        <span class="tweet-action">
                            <i class="fas fa-retweet text-success"></i>
                            <span>${tweet.retweets.toLocaleString()}</span>
                        </span>
                        <span class="tweet-action">
                            <i class="fas fa-reply text-info"></i>
                            <span>${tweet.replies.toLocaleString()}</span>
                        </span>
                    </div>
                    <div class="mt-2">
                        ${keywords}
                    </div>
                </div>
            </div>
        `;
    }

    formatTweetContent(content) {
        // 处理链接
        content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" class="text-primary">$1</a>');
        
        // 处理 @ 提及
        content = content.replace(/@(\w+)/g, '<a href="https://twitter.com/$1" target="_blank" class="text-primary">@$1</a>');
        
        // 处理 # 标签
        content = content.replace(/#(\w+)/g, '<a href="https://twitter.com/hashtag/$1" target="_blank" class="text-primary">#$1</a>');
        
        return content;
    }

    showTweetModal(tweetId) {
        const tweet = this.tweets.find(t => t.id === tweetId);
        if (!tweet) return;

        const modalBody = document.getElementById('tweet-modal-body');
        const tweetLink = document.getElementById('tweet-link');
        
        modalBody.innerHTML = `
            <div class="tweet-content mb-3">${this.formatTweetContent(tweet.content)}</div>
            <div class="tweet-meta mb-3">
                <i class="fab fa-twitter text-primary"></i> 
                <strong>@binance</strong> • ${new Date(tweet.date).toLocaleString('zh-CN')}
            </div>
            <div class="tweet-actions">
                <span class="tweet-action me-3">
                    <i class="fas fa-heart text-danger"></i>
                    <span>${tweet.likes.toLocaleString()} 点赞</span>
                </span>
                <span class="tweet-action me-3">
                    <i class="fas fa-retweet text-success"></i>
                    <span>${tweet.retweets.toLocaleString()} 转发</span>
                </span>
                <span class="tweet-action">
                    <i class="fas fa-reply text-info"></i>
                    <span>${tweet.replies.toLocaleString()} 回复</span>
                </span>
            </div>
            <div class="mt-3">
                <strong>相关关键词:</strong>
                <div class="mt-2">
                    ${tweet.keywords.map(keyword => 
                        `<span class="keyword-badge">${keyword}</span>`
                    ).join('')}
                </div>
            </div>
        `;
        
        tweetLink.href = tweet.url;
        
        const modal = new bootstrap.Modal(document.getElementById('tweetModal'));
        modal.show();
    }

    updateTweetCount() {
        const countElement = document.getElementById('tweet-count');
        countElement.textContent = `${this.filteredTweets.length} 条推文`;
    }

    getTimeAgo(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 60) {
            return `${minutes} 分钟前`;
        } else if (hours < 24) {
            return `${hours} 小时前`;
        } else {
            return `${days} 天前`;
        }
    }

    showUpdateNotification(totalTweets, airdropTweets) {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="fas fa-sync-alt"></i>
            <strong>数据已更新!</strong> 获取到 ${totalTweets} 条推文，其中 ${airdropTweets} 条空投相关
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <strong>错误!</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    startPeriodicUpdate() {
        // 每30秒检查一次连接状态
        setInterval(() => {
            if (!this.socket.connected) {
                this.updateConnectionStatus(false);
            }
        }, 30000);
    }
}

// 初始化应用
const app = new AirdropPlatform();
