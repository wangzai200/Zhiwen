# 测试配置和公共工具
import os
import sys
import pytest
import tempfile
from unittest.mock import Mock, patch
from api import app  # 假设 create_app 是创建 Flask 应用的函数

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 测试用的示例数据
SAMPLE_TEXT = """人工智能（Artificial Intelligence，简称AI）是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。
人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。"""

SAMPLE_SHORT_TEXT = "这是一个简短的测试文本。"

SAMPLE_EMPTY_TEXT = ""

# 测试配置
TEST_CONFIG = {
    'TESTING': True,
    'DEBUG': False,
    'SECRET_KEY': 'test-secret-key'
}


@pytest.fixture
def test_app():
    """直接复用现有app实例，动态修改配置"""
    # 临时覆盖生产配置
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'ALLOWED_IPS': ['*']  # 测试时禁用IP检查
    })

    # 临时放宽CORS限制
    app.config['CORS_RESOURCES'] = {
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST"]
        }
    }
    yield app


@pytest.fixture
def client(test_app):
    """创建测试客户端"""
    with test_app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def _auto_patch_dependencies(monkeypatch):
    """自动修补所有外部依赖"""
    # 模拟IP检查中间件（如果启用）
    monkeypatch.setattr(app, 'before_request_funcs', {})

    # 模拟核心业务逻辑
    def mock_generate_summary(text, sentences):
        return ["测试摘要" for _ in range(sentences)]

    def mock_generate(text, sentences):
        return "测试标题"

    monkeypatch.setattr('core.generate_summary', mock_generate_summary)
    monkeypatch.setattr('core.generator.generate', mock_generate)
