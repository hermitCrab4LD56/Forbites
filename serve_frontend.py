#!/usr/bin/env python3
"""
简单的HTTP服务器，用于提供前端文件
解决CORS问题，让前端可以正常访问后端API
"""

import http.server
import socketserver
import os
import sys

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.end_headers()

def main():
    # 设置端口
    PORT = 8000
    
    # 切换到前端目录
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    if not os.path.exists(frontend_dir):
        print(f"错误: 前端目录不存在: {frontend_dir}")
        sys.exit(1)
    
    os.chdir(frontend_dir)
    
    # 创建服务器
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"前端服务器启动在 http://localhost:{PORT}")
        print(f"请访问 http://localhost:{PORT} 来使用应用")
        print("确保后端服务器也在运行 (http://localhost:5001)")
        print("按 Ctrl+C 停止服务器")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")

if __name__ == "__main__":
    main() 