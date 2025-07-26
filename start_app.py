#!/usr/bin/env python3
"""
启动脚本 - 同时启动前端和后端服务器
"""

import subprocess
import sys
import os
import time
import threading
import signal

def start_backend():
    """启动后端服务器"""
    print("正在启动后端服务器...")
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    try:
        # 启动后端服务器
        process = subprocess.Popen([sys.executable, 'app.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # 等待服务器启动
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ 后端服务器启动成功 (http://localhost:5001)")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ 后端服务器启动失败:")
            print(stderr)
            return None
            
    except Exception as e:
        print(f"❌ 启动后端服务器时出错: {e}")
        return None

def start_frontend():
    """启动前端服务器"""
    print("正在启动前端服务器...")
    
    try:
        # 启动前端服务器
        process = subprocess.Popen([sys.executable, 'serve_frontend.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # 等待服务器启动
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ 前端服务器启动成功 (http://localhost:8000)")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ 前端服务器启动失败:")
            print(stderr)
            return None
            
    except Exception as e:
        print(f"❌ 启动前端服务器时出错: {e}")
        return None

def main():
    print("🚀 启动四时应用...")
    print("=" * 50)
    
    # 启动后端
    backend_process = start_backend()
    if not backend_process:
        print("❌ 无法启动后端服务器，应用启动失败")
        sys.exit(1)
    
    # 启动前端
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ 无法启动前端服务器，应用启动失败")
        backend_process.terminate()
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 应用启动成功!")
    print("📱 前端地址: http://localhost:8001")
    print("🔧 后端地址: http://localhost:5001")
    print("按 Ctrl+C 停止所有服务器")
    print("=" * 50)
    
    # 等待用户中断
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ 所有服务器已停止")

if __name__ == "__main__":
    main() 