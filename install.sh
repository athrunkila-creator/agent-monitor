#!/bin/bash
# Agent Monitor 安装脚本

set -e

echo "🦞 Agent Monitor 安装"
echo "====================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要安装 Python 3"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 安装依赖
echo "📥 安装依赖..."
./venv/bin/pip install requests --quiet

# 创建数据目录
mkdir -p data/exports

# 测试安装
echo "🧪 测试安装..."
./venv/bin/python cli.py status

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方式："
echo "  ./venv/bin/python cli.py status   # 显示状态"
echo "  ./venv/bin/python cli.py alerts   # 检查告警"
echo "  ./venv/bin/python cli.py export   # 导出数据"
echo "  ./venv/bin/python cli.py report   # 生成报告"