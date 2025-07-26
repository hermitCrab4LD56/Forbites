// 配置文件 - 管理不同环境的API地址
const CONFIG = {
    // 开发环境配置
    development: {
        apiBaseURL: 'http://localhost:5001/api',
        debug: true
    },
    
    // 生产环境配置
    production: {
        apiBaseURL: '/api',  // 相对路径，通过代理访问后端
        debug: false
    }
};

// 自动检测环境
function getConfig() {
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // 本地开发环境
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return CONFIG.development;
    }
    
    // 生产环境
    return CONFIG.production;
}

// 导出配置
window.APP_CONFIG = getConfig(); 