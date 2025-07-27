#!/bin/bash

echo "🚀 开始部署到Vercel..."

# 检查是否安装了Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI未安装，正在安装..."
    npm install -g vercel
fi

# 部署到Vercel
echo "📦 部署中..."
vercel --prod

echo "✅ 部署完成！"
echo "🌐 请访问: https://forbites.vercel.app" 