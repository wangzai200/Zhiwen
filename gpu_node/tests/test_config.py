"""
测试配置文件
定义各种测试场景和配置
"""

# 测试环境配置
TEST_ENVIRONMENTS = {
    'development': {
        'DEBUG': True,
        'TESTING': True,
        'SECRET_KEY': 'dev-test-key'
    },
    'ci': {
        'DEBUG': False,
        'TESTING': True,
        'SECRET_KEY': 'ci-test-key'
    },
    'production_test': {
        'DEBUG': False,
        'TESTING': True,
        'SECRET_KEY': 'prod-test-key'
    }
}

# 测试数据配置
TEST_DATA_CONFIG = {
    'short_text_length': 50,
    'medium_text_length': 500,
    'long_text_length': 5000,
    'max_text_length': 100000,
    'default_sentences': 3,
    'max_sentences': 100
}

# 性能测试配置
PERFORMANCE_CONFIG = {
    'max_response_time': 1.0,  # 秒
    'max_memory_usage': 50 * 1024 * 1024,  # 50MB
    'concurrent_requests': 10,
    'stress_test_iterations': 100,
    'large_text_size_mb': 1
}

# API测试配置
API_TEST_CONFIG = {
    'valid_endpoints': ['/summarize', '/title', '/nvidia_info'],
    'invalid_endpoints': ['/invalid', '/nonexistent'],
    'required_headers': {'Content-Type': 'application/json'},
    'cors_origins': ['http://127.0.0.1'],
    'allowed_methods': ['GET', 'POST', 'OPTIONS']
}

# Mock配置
MOCK_CONFIG = {
    'jiagu_mock_delay': 0.1,  # 模拟jiagu处理时间
    'model_mock_delay': 0.2,  # 模拟模型推理时间
    'nvidia_mock_info': {
        'driver_version': '525.60.11',
        'gpu_count': 1,
        'gpu_name': 'GeForce RTX 3080',
        'memory_total': 10737418240,
        'memory_free': 8589934592,
        'memory_used': 2147483648,
        'temperature': 45,
        'power_state': 0
    }
}

# 测试标记配置
TEST_MARKERS = {
    'unit': '单元测试 - 测试单个功能模块',
    'integration': '集成测试 - 测试模块间交互',
    'api': 'API测试 - 测试HTTP接口',
    'slow': '慢速测试 - 执行时间较长的测试',
    'performance': '性能测试 - 测试系统性能',
    'stress': '压力测试 - 测试系统在高负载下的表现'
}

# 覆盖率配置
COVERAGE_CONFIG = {
    'target_coverage': 85,  # 目标覆盖率百分比
    'exclude_files': [
        '*/tests/*',
        '*/venv/*',
        '*/checkpoint-*/*',
        '*/__pycache__/*'
    ],
    'exclude_lines': [
        'pragma: no cover',
        'def __repr__',
        'if self.debug:',
        'if settings.DEBUG',
        'raise AssertionError',
        'raise NotImplementedError',
        'if 0:',
        'if __name__ == .__main__.:'
    ]
}

# 测试报告配置
REPORT_CONFIG = {
    'html_report_dir': 'htmlcov',
    'xml_report_file': 'coverage.xml',
    'junit_report_file': 'test-results.xml',
    'json_report_file': 'test-results.json'
}
