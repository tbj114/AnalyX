#!/bin/bash

echo "========================================"
echo "  AnalyX - 快速启动脚本"
echo "========================================"
echo ""

echo "1. 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3，请先安装 Python 3.8 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Python 版本: $PYTHON_VERSION"
echo ""

echo "2. 安装依赖包..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败，请检查网络连接"
    exit 1
fi
echo "✅ 依赖包安装完成"
echo ""

echo "3. 启动 AnalyX..."
echo ""
python3 src/main.py
