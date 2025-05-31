#!/bin/bash
# 运行所有测试并生成覆盖率报告

# 确保在backend目录下运行
cd "$(dirname "$0")"

# 安装测试依赖
echo "安装测试依赖..."
pip install -r requirements.txt

# 运行测试并生成覆盖率报告
echo "运行测试..."
python -m pytest tests/ -v --cov=. --cov-report=term --cov-report=html:cov_report

# 如果测试成功，显示结果
if [ $? -eq 0 ]; then
    echo "测试成功完成！"
    echo "覆盖率报告已生成到 cov_report 目录"
    echo "使用浏览器打开 cov_report/index.html 可查看详细报告"
else
    echo "测试失败，请查看上方错误信息"
fi
