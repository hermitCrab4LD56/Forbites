@echo off
echo 🚀 开始部署到Vercel...

REM 检查是否安装了Vercel CLI
vercel --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Vercel CLI未安装，正在安装...
    npm install -g vercel
)

REM 部署到Vercel
echo 📦 部署中...
vercel --prod

echo ✅ 部署完成！
echo 🌐 请访问: https://forbites.vercel.app
pause 