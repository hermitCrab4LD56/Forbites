// 配置文件 - 管理不同环境的API地址
const CONFIG = {
    // 开发环境配置
    development: {
        apiBaseURL: 'http://localhost:5001/api',
        debug: true
    },
    
    // 生产环境配置（代理服务器）
    production: {
        apiBaseURL: '/api',  // 相对路径，通过代理访问后端
        debug: false
    },
    
    // 静态部署环境配置
    static: {
        apiBaseURL: 'https://forbites.vercel.app/api',  // Vercel部署的后端API
        debug: false
    },
    
    // 备用配置（如果代理不工作）
    fallback: {
        apiBaseURL: 'https://forbites.vercel.app/api',
        debug: true
    }
};

// 自动检测环境
function getConfig() {
    const hostname = window.location.hostname;
    const port = window.location.port;
    const pathname = window.location.pathname;
    
    console.log('环境检测:', { hostname, port, pathname, href: window.location.href });
    
    // 静态部署环境（直接访问frontend目录下的文件或forbites.store域名）
    if (pathname.includes('/frontend/') || hostname === 'www.forbites.store' || hostname === 'forbites.store') {
        console.log('使用静态部署环境配置');
        return CONFIG.static;
    }
    
    // 本地开发环境
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        console.log('使用开发环境配置');
        return CONFIG.development;
    }
    
    // 生产环境
    console.log('使用生产环境配置');
    return CONFIG.production;
}

// 导出配置
window.APP_CONFIG = getConfig();

// 测试API连接并自动回退
async function testAndFallbackConfig() {
    const config = window.APP_CONFIG;
    console.log('当前配置:', config);
    
    // 如果是生产环境，测试API连接
    if (config.apiBaseURL === '/api') {
        try {
            console.log('测试生产环境API连接...');
            const response = await fetch('/api/recipe/filters');
            if (!response.ok) {
                throw new Error(`API测试失败: ${response.status}`);
            }
            console.log('生产环境API连接成功');
        } catch (error) {
            console.warn('生产环境API连接失败，回退到备用配置:', error);
            window.APP_CONFIG = CONFIG.fallback;
            console.log('已切换到备用配置:', window.APP_CONFIG);
        }
    }
    
    // 如果是静态部署环境，测试API连接
    if (config.apiBaseURL.includes('forbites.vercel.app')) {
        try {
            console.log('测试静态部署环境API连接...');
            const response = await fetch(config.apiBaseURL + '/recipe/filters');
            if (!response.ok) {
                throw new Error(`API测试失败: ${response.status}`);
            }
            console.log('静态部署环境API连接成功');
        } catch (error) {
            console.warn('静态部署环境API连接失败，回退到备用配置:', error);
            window.APP_CONFIG = CONFIG.fallback;
            console.log('已切换到备用配置:', window.APP_CONFIG);
        }
    }
}

// 页面加载完成后测试配置
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', testAndFallbackConfig);
} else {
    testAndFallbackConfig();
} 