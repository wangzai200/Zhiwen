"""
API接口单元测试
测试Flask API的各个端点
"""
import pytest
import json
from unittest.mock import patch, Mock
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app
from .conftest import SAMPLE_TEXT, SAMPLE_SHORT_TEXT, TEST_CONFIG


class TestAPIEndpoints:
    """API端点测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app.config.update(TEST_CONFIG)
        with app.test_client() as client:
            yield client

    @pytest.mark.api
    def test_summarize_endpoint_success(self, client):
        """测试摘要接口正常情况"""
        with patch('api.generate_summary') as mock_generate:  # 关键修改：mock视图模块中的引用
            mock_generate.return_value = ["这是生成的摘要。"]  # 列表类型
            response = client.post('/summarize',
                                   json={'text': SAMPLE_TEXT, 'sentences': 2})
            assert response.status_code == 200
            data = response.get_json()
            assert 'summary' in data
            assert data['summary'] == ["这是生成的摘要。"]  # 断言列表
            assert data['sentence_count'] == 1  # 根据返回列表长度断言
            mock_generate.assert_called_once_with(SAMPLE_TEXT, 2)

    @pytest.mark.api
    def test_summarize_endpoint_default_sentences(self, client):
        """测试摘要接口默认句子数"""
        with patch('api.generate_summary') as mock_generate:  # 同样修正路径
            mock_generate.return_value = ["默认摘要1", "默认摘要2", "默认摘要3"]  # 默认3句子
            response = client.post('/summarize', json={'text': SAMPLE_TEXT})
            assert response.status_code == 200
            data = response.get_json()
            assert data['sentence_count'] == 3  # 断言句子数正确
            mock_generate.assert_called_once_with(SAMPLE_TEXT, 3)  # 验证默认参数3
    
    @pytest.mark.api
    def test_summarize_endpoint_missing_text(self, client):
        """测试摘要接口缺少text参数"""
        response = client.post('/summarize', json={'sentences': 2})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert "Missing required parameter 'text'" in data['error']
    
    @pytest.mark.api
    def test_summarize_endpoint_invalid_json(self, client):
        """测试摘要接口无效JSON"""
        response = client.post('/summarize', json=None)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    @pytest.mark.api
    def test_summarize_endpoint_value_error(self, client):
        """测试摘要接口值错误处理"""
        with patch('api.generate_summary') as mock_generate:
            mock_generate.side_effect = ValueError("Sentences count must be a positive integer")

            response = client.post('/summarize',
                                 json={'text': SAMPLE_TEXT, 'sentences': -1})
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
            assert "Sentences count must be a positive integer" in data['error']
    
    @pytest.mark.api
    def test_summarize_endpoint_internal_error(self, client):
        """测试摘要接口内部错误处理"""
        with patch('api.generate_summary') as mock_generate:
            mock_generate.side_effect = Exception("Internal error")
            
            response = client.post('/summarize', json={'text': SAMPLE_TEXT})
            
            assert response.status_code == 500
            data = response.get_json()
            assert 'error' in data
            assert "Internal server error" in data['error']
    
    @pytest.mark.api
    def test_title_endpoint_success(self, client):
        """测试标题生成接口正常情况"""
        with patch('api.generator.generate') as mock_generate:
            mock_generate.return_value = ["生成的标题1", "生成的标题2"]
            
            response = client.post('/title', 
                                 json={'text': SAMPLE_TEXT, 'sentences': 2})
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'title' in data
            assert data['title'] == ["生成的标题1", "生成的标题2"]
            mock_generate.assert_called_once_with(SAMPLE_TEXT, 2)
    
    @pytest.mark.api
    def test_title_endpoint_default_sentences(self, client):
        """测试标题生成接口默认句子数"""
        with patch('api.generator.generate') as mock_generate:
            mock_generate.return_value = ["默认标题"]
            
            response = client.post('/title', json={'text': SAMPLE_TEXT})
            
            assert response.status_code == 200
            mock_generate.assert_called_once_with(SAMPLE_TEXT, 3)
    
    @pytest.mark.api
    def test_title_endpoint_missing_text(self, client):
        """测试标题生成接口缺少text参数"""
        response = client.post('/title', json={'sentences': 2})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert "Missing required parameter 'text'" in data['error']
    
    @pytest.mark.api
    def test_title_endpoint_value_error(self, client):
        """测试标题生成接口值错误处理"""
        with patch('api.generator.generate') as mock_generate:
            mock_generate.side_effect = ValueError("Invalid title count")
            
            response = client.post('/title', 
                                 json={'text': SAMPLE_TEXT, 'sentences': -1})
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
            assert "Invalid title count" in data['error']
    
    @pytest.mark.api
    def test_title_endpoint_internal_error(self, client):
        """测试标题生成接口内部错误处理"""
        with patch('api.generator.generate') as mock_generate:
            mock_generate.side_effect = Exception("Internal error")
            
            response = client.post('/title', json={'text': SAMPLE_TEXT})
            
            assert response.status_code == 500
            data = response.get_json()
            assert 'error' in data
            assert "Internal server error" in data['error']
    
    @pytest.mark.api
    def test_nvidia_info_endpoint_success(self, client):
        """测试NVIDIA信息接口正常情况"""
        with patch('api.nvmlInit'), \
             patch('api.nvmlSystemGetDriverVersion', return_value="525.60.11"), \
             patch('api.nvmlDeviceGetCount', return_value=1), \
             patch('api.nvmlDeviceGetHandleByIndex') as mock_handle, \
             patch('api.nvmlDeviceGetMemoryInfo') as mock_memory, \
             patch('api.nvmlDeviceGetName', return_value="GeForce RTX 3080"), \
             patch('api.nvmlDeviceGetTemperature', return_value=45), \
             patch('api.nvmlDeviceGetPowerState', return_value=0), \
             patch('api.nvmlShutdown'):
            
            # 模拟内存信息
            mock_memory_info = Mock()
            mock_memory_info.total = 10737418240  # 10GB
            mock_memory_info.free = 8589934592    # 8GB
            mock_memory_info.used = 2147483648    # 2GB
            mock_memory.return_value = mock_memory_info
            
            response = client.get('/nvidia_info')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['state'] is True
            assert data['nvidia_version'] == "525.60.11"
            assert data['nvidia_count'] == 1
            assert len(data['gpus']) == 1
            
            gpu = data['gpus'][0]
            assert gpu['gpu_name'] == "GeForce RTX 3080"
            assert gpu['total'] == 10737418240
            assert gpu['free'] == 8589934592
            assert gpu['used'] == 2147483648
            assert gpu['temperature'] == "45℃"
            assert gpu['powerStatus'] == 0
    
    @pytest.mark.api
    def test_nvidia_info_endpoint_nvml_error(self, client):
        """测试NVIDIA信息接口NVML错误"""
        with patch('api.nvmlInit') as mock_init:
            from pynvml import NVMLError
            mock_init.side_effect = NVMLError("NVML not available")
            
            response = client.get('/nvidia_info')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['state'] is False
    
    @pytest.mark.api
    def test_nvidia_info_endpoint_general_error(self, client):
        """测试NVIDIA信息接口一般错误"""
        with patch('api.nvmlInit') as mock_init:
            mock_init.side_effect = Exception("General error")
            
            response = client.get('/nvidia_info')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['state'] is False
    
    @pytest.mark.api
    def test_invalid_endpoint(self, client):
        """测试无效端点"""
        response = client.get('/invalid_endpoint')
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_wrong_http_method(self, client):
        """测试错误的HTTP方法"""
        response = client.get('/summarize')
        assert response.status_code == 405
        
        response = client.get('/title')
        assert response.status_code == 405
