#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
依赖安装脚本
"""

import subprocess
import sys
import os

def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ {package} 安装失败")
        return False

def main():
    """主安装函数"""
    print("开始安装四时美食应用依赖...")
    print("=" * 50)
    
    # 核心依赖
    core_packages = [
        "Flask==2.2.5",
        "flask-cors==4.0.0", 
        "Flask-SQLAlchemy==3.0.5",
        "python-dotenv==0.21.1",
        "requests==2.28.2",
        "SQLAlchemy==1.4.46"
    ]
    
    # 可选依赖（语音识别相关）
    # 注意：语音识别功能使用百度智能云API，不需要本地语音识别库
    optional_packages = []
    
    print("安装核心依赖...")
    core_success = 0
    for package in core_packages:
        if install_package(package):
            core_success += 1
    
    print(f"\n核心依赖安装结果: {core_success}/{len(core_packages)} 成功")
    
    if core_success == len(core_packages):
        print("\n✓ 核心依赖安装完成！应用可以正常运行。")
    else:
        print("\n❌ 核心依赖安装失败，请检查网络连接或Python环境。")
        return False
    
    print("\n语音识别功能说明...")
    print("✓ 语音识别功能使用百度智能云API实现")
    print("✓ 不需要本地语音识别库")
    print("✓ 只需要配置百度API密钥即可使用")
    
    print("\n" + "=" * 50)
    print("安装完成！")
    print("\n下一步：")
    print("1. 创建 .env 文件并配置API密钥")
    print("2. 运行 python app.py 启动后端服务")
    print("3. 在浏览器中打开前端页面")
    
    return True

if __name__ == "__main__":
    main() 