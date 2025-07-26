#!/usr/bin/env python3
"""
简单的HTTP服务器，用于提供前端文件并代理API请求
解决CORS问题，让前端可以正常访问后端API
"""

import http.server
import socketserver
import os
import sys
import urllib.request
import urllib.parse
import json

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
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
    
    def do_GET(self):
        # 检查是否是API请求
        if self.path.startswith('/api/'):
            self.proxy_api_request('GET')
        else:
            super().do_GET()
    
    def do_POST(self):
        # 检查是否是API请求
        if self.path.startswith('/api/'):
            self.proxy_api_request('POST')
        else:
            super().do_POST()
    
    def do_PUT(self):
        # 检查是否是API请求
        if self.path.startswith('/api/'):
            self.proxy_api_request('PUT')
        else:
            super().do_PUT()
    
    def do_DELETE(self):
        # 检查是否是API请求
        if self.path.startswith('/api/'):
            self.proxy_api_request('DELETE')
        else:
            super().do_DELETE()
    
    def proxy_api_request(self, method):
        """代理API请求到后端服务器"""
        try:
            # 构建后端URL
            backend_url = f"http://localhost:5001{self.path}"
            
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = None
            if content_length > 0:
                post_data = self.rfile.read(content_length)
            
            # 创建请求
            req = urllib.request.Request(backend_url, data=post_data, method=method)
            
            # 复制请求头
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'content-length']:
                    req.add_header(header, value)
            
            # 发送请求到后端
            with urllib.request.urlopen(req) as response:
                # 读取响应
                response_data = response.read()
                
                # 发送响应
                self.send_response(response.status)
                
                # 复制响应头
                for header, value in response.getheaders():
                    if header.lower() not in ['server', 'date']:
                        self.send_header(header, value)
                
                self.end_headers()
                self.wfile.write(response_data)
                
        except Exception as e:
            print(f"代理请求失败: {e}")
            self.send_error(502, f"Bad Gateway: {str(e)}")

def main():
    # 设置端口
    PORT = 8001
    
    # 切换到前端目录
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    if not os.path.exists(frontend_dir):
        print(f"错误: 前端目录不存在: {frontend_dir}")
        sys.exit(1)
    
    os.chdir(frontend_dir)
    
    # 创建服务器
    with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
        print(f"前端服务器启动在 http://localhost:{PORT}")
        print(f"请访问 http://localhost:{PORT} 来使用应用")
        print("API请求将自动代理到后端服务器 (http://localhost:5001)")
        print("按 Ctrl+C 停止服务器")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")

if __name__ == "__main__":
    main() 