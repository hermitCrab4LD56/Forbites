#!/bin/bash

echo "🚀 开始部署四时应用到Vercel..."

# 检查是否安装了Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI未安装，正在安装..."
    npm install -g vercel
fi

# 检查是否已登录
if ! vercel whoami &> /dev/null; then
    echo "🔐 请先登录Vercel..."
    vercel login
fi

# 部署到生产环境
echo "📦 部署到生产环境..."
vercel --prod

echo "✅ 部署完成！"
echo "🌐 API地址: https://forbites.vercel.app/api"
echo "📱 前端地址: https://www.forbites.store"
echo ""
echo "🧪 测试API:"
echo "curl https://forbites.vercel.app/api/health" 