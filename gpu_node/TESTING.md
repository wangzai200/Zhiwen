# GPU Node 项目测试指南

## 概述

本项目包含完整的单元测试套件，涵盖API接口、核心功能模块、集成测试和性能测试。

## 测试结构

```
tests/
├── conftest.py              # 测试配置和公共工具
├── test_api.py             # API接口测试
├── test_summary.py         # 摘要功能测试
├── test_title.py           # 标题生成测试
├── test_integration.py     # 集成测试
├── test_performance.py     # 性能测试
├── test_validation.py      # 数据验证测试
├── test_utils.py          # 测试工具函数
└── test_config.py         # 测试配置
```

## 快速开始

### 1. 安装测试依赖

```bash
# 安装测试依赖包
pip install -r requirements-test.txt
```

### 2. 运行所有测试

#### Windows (推荐)
```cmd
# 使用批处理脚本（推荐）
test.bat

# 或使用Python脚本
python run_tests.py
```

#### Linux/Mac
```bash
# 直接使用pytest
pytest tests/

# 或使用Python脚本
python run_tests.py
```

## 测试命令详解

### 基本测试命令

```cmd
# 运行所有测试
test.bat

# 运行特定类型的测试
test.bat --unit           # 单元测试
test.bat --integration    # 集成测试
test.bat --api           # API测试
test.bat --slow          # 慢速测试

# 运行性能测试
test.bat --performance

# 禁用覆盖率报告
test.bat --no-coverage
```

### 环境检查和依赖管理

```cmd
# 检查测试环境
test.bat --check-env

# 安装测试依赖
test.bat --install-deps

# 生成详细测试报告
test.bat --report
```

### 高级选项

```cmd
# 使用pytest直接运行
pytest tests/ -v                    # 详细输出
pytest tests/ -x                    # 遇到第一个失败就停止
pytest tests/ -k "test_api"         # 运行包含"test_api"的测试
pytest tests/test_api.py::TestAPIEndpoints::test_summarize_endpoint_success  # 运行特定测试
```

## 测试类型说明

### 单元测试 (Unit Tests)
- **标记**: `@pytest.mark.unit`
- **描述**: 测试单个函数或类的功能
- **覆盖范围**: 
  - `core.summary.generate_summary()`
  - `core.title.title.TitleGenerator`
  - 工具函数和辅助方法

### 集成测试 (Integration Tests)
- **标记**: `@pytest.mark.integration`
- **描述**: 测试模块间的交互和数据流
- **覆盖范围**: 
  - API端点与核心模块的集成
  - 多组件协同工作
  - 端到端功能测试

### API测试 (API Tests)
- **标记**: `@pytest.mark.api`
- **描述**: 测试HTTP API接口
- **覆盖范围**: 
  - `/summarize` 端点
  - `/title` 端点
  - `/nvidia_info` 端点
  - 错误处理和状态码

### 性能测试 (Performance Tests)
- **标记**: `@pytest.mark.slow`
- **描述**: 测试系统性能和稳定性
- **覆盖范围**: 
  - 响应时间测试
  - 内存使用测试
  - 并发请求测试
  - 压力测试

## 测试报告

### 覆盖率报告

测试完成后，会生成以下报告：

1. **HTML报告**: `htmlcov/index.html`
   - 可视化覆盖率报告
   - 可以查看具体哪些代码行被测试覆盖

2. **终端报告**: 
   - 实时显示覆盖率统计
   - 显示未覆盖的代码行

3. **XML报告**: `coverage.xml`
   - 用于CI/CD集成
   - 机器可读格式

### JUnit报告

生成 `test-results.xml` 文件，包含：
- 测试执行时间
- 测试通过/失败统计
- 详细的错误信息

## 测试配置

### pytest.ini
项目根目录的 `pytest.ini` 文件配置了：
- 测试发现路径
- 覆盖率设置
- 测试标记
- 输出格式

### 测试标记

使用 `-m` 参数运行特定标记的测试：

```bash
pytest -m unit          # 只运行单元测试
pytest -m "not slow"    # 跳过慢速测试
pytest -m "api or integration"  # 运行API或集成测试
```

## Mock和模拟

测试中广泛使用Mock来：
- 隔离被测试的组件
- 模拟外部依赖（如GPU硬件）
- 控制测试数据和条件
- 提高测试执行速度

### 常用Mock示例

```python
# 模拟jiagu摘要生成
with patch('core.summary.jiagu.summarize') as mock_summarize:
    mock_summarize.return_value = "模拟摘要结果"
    # 执行测试...

# 模拟标题生成器
with patch('core.generator.generate') as mock_generate:
    mock_generate.return_value = ["模拟标题1", "模拟标题2"]
    # 执行测试...
```

## 持续集成 (CI)

### GitHub Actions 示例

创建 `.github/workflows/test.yml`:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - run: pip install -r requirements-test.txt
    - run: python run_tests.py --type all
    - uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

## 故障排除

### 常见问题

1. **导入错误**
   ```
   解决方案: 确保在项目根目录运行测试
   cd d:\03_Projects\Zhiwen_Finish\gpu_node
   ```

2. **依赖缺失**
   ```
   解决方案: 安装测试依赖
   test.bat --install-deps
   ```

3. **CUDA相关错误**
   ```
   解决方案: 测试中已使用Mock，不需要真实GPU
   ```

4. **覆盖率过低**
   ```
   解决方案: 检查exclude配置，添加更多测试用例
   ```

### 调试测试

```bash
# 运行单个测试文件
pytest tests/test_api.py -v

# 运行特定测试方法
pytest tests/test_api.py::TestAPIEndpoints::test_summarize_endpoint_success -v

# 添加调试输出
pytest tests/test_api.py -v -s

# 在第一个失败处停止
pytest tests/test_api.py -x
```

## 最佳实践

1. **编写新测试时**:
   - 使用描述性的测试名称
   - 添加适当的测试标记
   - 包含边界条件测试
   - 使用Mock隔离外部依赖

2. **维护测试时**:
   - 保持测试独立性
   - 清理测试产生的临时文件
   - 更新测试数据和预期结果

3. **运行测试时**:
   - 定期运行完整测试套件
   - 在提交代码前运行相关测试
   - 监控测试覆盖率变化

## 联系方式

如有测试相关问题，请查看：
- 测试日志和错误信息
- 本文档的故障排除部分
- 项目的其他文档
