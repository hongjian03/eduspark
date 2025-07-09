#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用启动脚本
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """检查依赖是否安装"""
    try:
        import streamlit
        import langchain
        import pandas
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_config():
    """检查配置文件"""
    secrets_file = Path(".streamlit/secrets.toml")
    if secrets_file.exists():
        print("✅ 配置文件存在")
        return True
    else:
        print("⚠️ 配置文件不存在，请创建 .streamlit/secrets.toml 并配置API密钥")
        return False

def main():
    """主函数"""
    print("🚀 启动留学标签识别应用")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        sys.exit(1)
    
    # 检查配置
    check_config()
    
    print("\n🌐 启动Streamlit应用...")
    print("应用将在浏览器中自动打开")
    print("按 Ctrl+C 停止应用")
    print("=" * 50)
    
    # 启动streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except FileNotFoundError:
        print("❌ Streamlit未安装，请运行: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main() 