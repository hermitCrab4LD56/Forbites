#!/usr/bin/env python3
"""
Vercel API入口文件
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# 导入Flask应用
from app import app

# 导出应用实例供Vercel使用
if __name__ == "__main__":
    app.run() 