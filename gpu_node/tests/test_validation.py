"""
数据验证和边界测试
测试各种边界条件和数据验证
"""
import pytest
from unittest.mock import patch, Mock
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app
from core.summary import generate_summary
from .conftest import TEST_CONFIG


class TestDataValidation:
    """数据验证测试类"""

    @pytest.fixture
    def client(self):
        app.config.update(TEST_CONFIG)
        with app.test_client() as client:
            yield client

    @pytest.mark.unit
    def test_empty_text_validation(self, client):
        """测试空文本验证"""
        response = client.post('/summarize', json={'text': '', 'sentences': 3})
        assert response.status_code == 400
        data = response.get_json()
        assert "empty or whitespace" in data['error']

    @pytest.mark.unit
    def test_whitespace_only_text(self, client):
        """测试仅包含空白字符的文本"""
        response = client.post('/summarize', json={'text': '   \n\t\r   ', 'sentences': 2})
        assert response.status_code == 400
        data = response.get_json()
        assert "empty or whitespace" in data['error']

    @pytest.mark.unit
    def test_special_characters_text(self, client):
        """测试包含特殊字符的文本"""
        with patch('api.generate_summary') as mock_summary:
            mock_summary.return_value = ["特殊字符测试结果"]
            response = client.post('/summarize',
                                   json={'text': '特殊字符测试: !@#$%^&*()_+-=[]{}|;\':",./<>?', 'sentences': 1})
            assert response.status_code == 200
            assert response.get_json()['summary'] == ['特殊字符测试结果']

    @pytest.mark.unit
    def test_mixed_language_text(self, client):
        """测试混合语言文本"""
        with patch('api.generate_summary') as mock_summary:
            mock_summary.return_value = ["混合语言摘要"]
            response = client.post('/summarize',
                                   json={'text': '这是中文 This is English これは日本語です', 'sentences': 2})
            assert response.status_code == 200
            assert response.get_json()['summary'] == ["混合语言摘要"]

    @pytest.mark.unit
    def test_sentences_boundary_values(self, client):
        """测试句子数边界值"""
        test_text = "测试边界值文本。第一句。第二句。第三句。第四句。"

        # 测试最小值
        response = client.post('/summarize', json={'text': test_text, 'sentences': 0})
        assert response.status_code == 400

        # 测试正常值
        with patch('api.generate_summary') as mock_summary:
            mock_summary.return_value = ["摘要1", "摘要2"]
            response = client.post('/summarize', json={'text': test_text, 'sentences': 2})
            assert response.status_code == 200
            assert len(response.get_json()['summary']) == 2

        # 测试较大值
        with patch('api.generate_summary') as mock_summary:
            mock_summary.return_value = ["摘要1", "摘要2", "摘要3", "摘要4"]
            response = client.post('/summarize', json={'text': test_text, 'sentences': 100})
            assert response.status_code == 200
            assert len(response.get_json()['summary']) == 4


class TestBoundaryConditions:
    """边界条件测试类"""

    @pytest.mark.unit
    def test_maximum_text_length(self, client):
        """测试最大文本长度处理"""
        long_text = "长文本测试。" * 10000
        with patch('api.generate_summary') as mock_summary:
            mock_summary.return_value = ["长文本摘要"]
            response = client.post('/summarize', json={'text': long_text, 'sentences': 1})
            assert response.status_code == 200

    @pytest.mark.unit
    def test_control_characters(self, client):
        """测试控制字符处理"""
        with patch('api.generate_summary') as mock_summary:
            mock_summary.return_value = ["控制字符摘要"]
            response = client.post('/summarize',
                                   json={'text': '测试\x00\x01控制字符', 'sentences': 1})
            assert response.status_code == 200

    @pytest.mark.unit
    def test_html_content_handling(self, client):
        """测试HTML内容处理"""
        with patch('api.generate_summary') as mock_summary:
            mock_summary.return_value = ["HTML摘要"]
            response = client.post('/summarize',
                                   json={'text': '<div>测试内容</div>', 'sentences': 1})
            assert response.status_code == 200
