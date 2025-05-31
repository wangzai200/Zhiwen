"""
主测试运行脚本
提供便捷的测试运行和报告生成功能
"""
import subprocess
import sys
import os
import argparse
from pathlib import Path


def run_tests(test_type="all", coverage=True, verbose=True, output_format="html"):
    """
    运行测试套件
    
    Args:
        test_type: 测试类型 ("all", "unit", "integration", "api", "slow")
        coverage: 是否生成覆盖率报告
        verbose: 是否显示详细输出
        output_format: 报告格式 ("html", "xml", "json")
    """
    # 基础命令
    cmd = ["python", "-m", "pytest"]
    
    # 添加测试路径
    cmd.append("tests/")
    
    # 根据测试类型添加标记
    if test_type != "all":
        cmd.extend(["-m", test_type])
    
    # 添加覆盖率选项
    if coverage:
        cmd.extend([
            "--cov=.",
            "--cov-report=term-missing",
            f"--cov-report={output_format}"
        ])
    
    # 添加详细输出
    if verbose:
        cmd.append("-v")
    
    # 添加其他有用的选项
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    print(f"运行命令: {' '.join(cmd)}")
    print("-" * 60)
    
    # 执行测试
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, check=True)
        print("\n✅ 测试执行成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 测试执行失败，退出码: {e.returncode}")
        return False


def install_dependencies():
    """安装测试依赖"""
    print("安装测试依赖...")
    
    try:
        subprocess.run([
            "pip", "install", "-r", "requirements-test.txt"
        ], check=True)
        print("✅ 测试依赖安装成功!")
        return True
    except subprocess.CalledProcessError:
        print("❌ 测试依赖安装失败!")
        return False


def generate_test_report():
    """生成测试报告"""
    print("生成详细测试报告...")
    
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--cov=.",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--junitxml=test-results.xml",
        "-v"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 测试报告生成成功!")
        print("📊 HTML报告: htmlcov/index.html")
        print("📊 XML报告: coverage.xml")
        print("📊 JUnit报告: test-results.xml")
        return True
    except subprocess.CalledProcessError:
        print("❌ 测试报告生成失败!")
        return False


def run_specific_tests(test_files):
    """运行指定的测试文件"""
    cmd = ["python", "-m", "pytest"] + test_files + ["-v"]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 指定测试执行成功!")
        return True
    except subprocess.CalledProcessError:
        print("❌ 指定测试执行失败!")
        return False


def run_performance_tests():
    """运行性能测试"""
    print("运行性能测试（这可能需要一些时间）...")
    
    cmd = [
        "python", "-m", "pytest",
        "tests/test_performance.py",
        "-m", "slow",
        "-v",
        "--tb=short"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 性能测试完成!")
        return True
    except subprocess.CalledProcessError:
        print("❌ 性能测试失败!")
        return False


def check_test_environment():
    """检查测试环境"""
    print("检查测试环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("⚠️  警告: Python版本可能过旧，建议使用Python 3.7+")
    
    # 检查必要的包
    required_packages = ['pytest', 'flask', 'torch']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行 'pip install -r requirements-test.txt' 安装依赖")
        return False
    
    # 检查项目结构
    required_files = ['api.py', 'core/', 'tests/']
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"缺少必要文件/目录: {', '.join(missing_files)}")
        return False
    
    print("✅ 测试环境检查通过!")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GPU Node 项目测试运行器")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "api", "slow"],
        default="all",
        help="要运行的测试类型"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="禁用覆盖率报告"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="安装测试依赖"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成详细测试报告"
    )
    parser.add_argument(
        "--performance",
        action="store_true",
        help="运行性能测试"
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="检查测试环境"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="运行指定的测试文件"
    )
    
    args = parser.parse_args()
    
    # 改变到项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    success = True
    
    # 检查环境
    if args.check_env:
        success = check_test_environment() and success
        return 0 if success else 1
    
    # 安装依赖
    if args.install_deps:
        success = install_dependencies() and success
    
    # 运行指定文件的测试
    if args.files:
        success = run_specific_tests(args.files) and success
    
    # 运行性能测试
    elif args.performance:
        success = run_performance_tests() and success
    
    # 生成报告
    elif args.report:
        success = generate_test_report() and success
    
    # 运行常规测试
    else:
        success = run_tests(
            test_type=args.type,
            coverage=not args.no_coverage
        ) and success
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
