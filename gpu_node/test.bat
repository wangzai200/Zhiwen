@echo off
REM GPU Node 项目测试运行脚本 (Windows)
REM 使用方法: test.bat [选项]

setlocal enabledelayedexpansion

REM 设置默认参数
set TEST_TYPE=all
set COVERAGE=true
set INSTALL_DEPS=false
set GENERATE_REPORT=false
set CHECK_ENV=false
set PERFORMANCE=false

REM 解析命令行参数
:parse_args
if "%1"=="" goto run_tests
if "%1"=="--unit" (
    set TEST_TYPE=unit
    shift
    goto parse_args
)
if "%1"=="--integration" (
    set TEST_TYPE=integration
    shift
    goto parse_args
)
if "%1"=="--api" (
    set TEST_TYPE=api
    shift
    goto parse_args
)
if "%1"=="--slow" (
    set TEST_TYPE=slow
    shift
    goto parse_args
)
if "%1"=="--no-coverage" (
    set COVERAGE=false
    shift
    goto parse_args
)
if "%1"=="--install-deps" (
    set INSTALL_DEPS=true
    shift
    goto parse_args
)
if "%1"=="--report" (
    set GENERATE_REPORT=true
    shift
    goto parse_args
)
if "%1"=="--check-env" (
    set CHECK_ENV=true
    shift
    goto parse_args
)
if "%1"=="--performance" (
    set PERFORMANCE=true
    shift
    goto parse_args
)
if "%1"=="--help" (
    goto show_help
)
echo 未知参数: %1
goto show_help

:show_help
echo.
echo GPU Node 测试运行器
echo.
echo 使用方法: test.bat [选项]
echo.
echo 选项:
echo   --unit           运行单元测试
echo   --integration    运行集成测试
echo   --api           运行API测试
echo   --slow          运行慢速测试
echo   --performance   运行性能测试
echo   --no-coverage   禁用覆盖率报告
echo   --install-deps  安装测试依赖
echo   --report        生成详细报告
echo   --check-env     检查测试环境
echo   --help          显示此帮助信息
echo.
echo 示例:
echo   test.bat                    # 运行所有测试
echo   test.bat --unit             # 只运行单元测试
echo   test.bat --install-deps     # 安装依赖并运行测试
echo   test.bat --report           # 生成详细报告
echo   test.bat --check-env        # 检查测试环境
echo.
goto end

:run_tests
echo.
echo ========================================
echo GPU Node 项目测试运行器
echo ========================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请确保Python已安装并在PATH中
    goto error_exit
)

REM 检查是否在正确的目录
if not exist "api.py" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    goto error_exit
)

REM 检查测试目录是否存在
if not exist "tests" (
    echo ❌ 错误: 未找到tests目录
    echo 💡 请先创建测试目录结构，或运行 create_test_structure.bat
    goto error_exit
)

REM 安装依赖
if "%INSTALL_DEPS%"=="true" (
    echo 📦 安装测试依赖...
    pip install -r requirements-test.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        goto error_exit
    )
    echo ✅ 依赖安装成功
    echo.
)

REM 检查环境
if "%CHECK_ENV%"=="true" (
    echo 🔍 检查测试环境...
    python run_tests.py --check-env
    if errorlevel 1 (
        echo ❌ 环境检查失败
        goto error_exit
    )
    goto success_exit
)

REM 运行性能测试
if "%PERFORMANCE%"=="true" (
    echo 🚀 运行性能测试...
    python run_tests.py --performance
    if errorlevel 1 (
        echo ❌ 性能测试失败
        goto error_exit
    )
    goto success_exit
)

REM 生成详细报告
if "%GENERATE_REPORT%"=="true" (
    echo 📊 生成详细测试报告...
    python run_tests.py --report
    if errorlevel 1 (
        echo ❌ 报告生成失败
        goto error_exit
    )
    echo.
    echo 📊 报告已生成:
    echo    - HTML报告: htmlcov\index.html
    echo    - XML报告: coverage.xml
    echo    - JUnit报告: test-results.xml
    goto success_exit
)

REM 运行常规测试
echo 🧪 运行测试: %TEST_TYPE%
if "%COVERAGE%"=="true" (
    echo 📈 包含覆盖率报告
)
echo.

REM 构建测试命令
set CMD=python run_tests.py --type %TEST_TYPE%
if "%COVERAGE%"=="false" (
    set CMD=!CMD! --no-coverage
)

REM 执行测试
%CMD%
if errorlevel 1 (
    echo.
    echo ❌ 测试执行失败
    goto error_exit
)

:success_exit
echo.
echo ✅ 测试执行成功!
echo.
echo 💡 提示:
echo    - 查看详细报告: test.bat --report
echo    - 检查环境: test.bat --check-env
echo    - 运行性能测试: test.bat --performance
echo.
goto end

:error_exit
echo.
echo ❌ 测试执行失败!
echo.
echo 💡 故障排除:
echo    1. 检查Python环境: test.bat --check-env
echo    2. 安装依赖: test.bat --install-deps
echo    3. 查看帮助: test.bat --help
echo.
exit /b 1

:end
endlocal
