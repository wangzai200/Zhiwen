"""
集成测试
测试各模块之间的集成和端到端功能
"""
import pytest
import json
import sys
import os
from unittest.mock import patch, Mock

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app
from .conftest import SAMPLE_TEXT, TEST_CONFIG


class TestIntegration:
    """集成测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app.config.update(TEST_CONFIG)
        with app.test_client() as client:
            yield client
    
    @pytest.mark.integration
    def test_summarize_title_workflow(self, client):
        """测试摘要和标题生成的完整工作流程"""
        # 模拟摘要生成
        with patch('core.generate_summary') as mock_summary:
            mock_summary.return_value = "这是生成的摘要。"
            
            summary_response = client.post('/summarize', 
                                         json={'text': SAMPLE_TEXT, 'sentences': 2})
            
            assert summary_response.status_code == 200
            summary_data = summary_response.get_json()
            assert 'summary' in summary_data
        
        # 模拟标题生成
        with patch('core.generator.generate') as mock_title:
            mock_title.return_value = ["生成的标题1", "生成的标题2"]
            
            title_response = client.post('/title', 
                                       json={'text': SAMPLE_TEXT, 'sentences': 2})
            
            assert title_response.status_code == 200
            title_data = title_response.get_json()
            assert 'title' in title_data
            assert len(title_data['title']) == 2
    
    @pytest.mark.integration
    def test_error_handling_consistency(self, client):
        """测试错误处理的一致性"""
        # 测试所有端点对缺少参数的处理
        endpoints = ['/summarize', '/title']
        
        for endpoint in endpoints:
            response = client.post(endpoint, json={})
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
            assert "Missing required parameter 'text'" in data['error']
    
    @pytest.mark.integration
    def test_multiple_requests_stability(self, client):
        """测试多个请求的稳定性"""
        with patch('core.generate_summary') as mock_summary, \
             patch('core.generator.generate') as mock_title:
            
            mock_summary.return_value = "稳定性测试摘要。"
            mock_title.return_value = ["稳定性测试标题"]
            
            # 发送多个请求
            for i in range(5):
                summary_response = client.post('/summarize', 
                                             json={'text': f"测试文本{i}", 'sentences': 1})
                assert summary_response.status_code == 200
                
                title_response = client.post('/title', 
                                           json={'text': f"测试文本{i}", 'sentences': 1})
                assert title_response.status_code == 200
    
    @pytest.mark.integration
    def test_cors_headers(self, client):
        """测试CORS头部设置"""
        response = client.options('/summarize')
        
        # 检查CORS相关头部
        assert response.status_code in [200, 204]  # OPTIONS通常返回204
    
    @pytest.mark.integration
    def test_content_type_handling(self, client):
        """测试不同Content-Type的处理"""
        with patch('core.generate_summary') as mock_summary:
            mock_summary.return_value = "内容类型测试。"
            
            # 测试正确的JSON Content-Type
            response = client.post('/summarize',
                                 data=json.dumps({'text': SAMPLE_TEXT}),
                                 content_type='application/json')
            assert response.status_code == 200
            
            # 测试错误的Content-Type
            response = client.post('/summarize',
                                 data="text=test",
                                 content_type='application/x-www-form-urlencoded')
            assert response.status_code == 400
    
    @pytest.mark.integration
    def test_large_text_handling(self, client):
        """测试大文本处理"""
        # 创建较大的文本
        large_text = SAMPLE_TEXT * 100
        
        with patch('core.generate_summary') as mock_summary, \
             patch('core.generator.generate') as mock_title:
            
            mock_summary.return_value = "大文本摘要。"
            mock_title.return_value = ["大文本标题"]
            
            # 测试摘要接口
            response = client.post('/summarize', 
                                 json={'text': large_text, 'sentences': 3})
            assert response.status_code == 200
            
            # 测试标题接口
            response = client.post('/title', 
                                 json={'text': large_text, 'sentences': 2})
            assert response.status_code == 200
    
    @pytest.mark.integration
    def test_unicode_text_handling(self, client):
        """测试Unicode文本处理"""
        unicode_text = "这是一个包含中文、English、数字123和emoji😀的测试文本。"
        
        with patch('api.generate_summary') as mock_summary, \
             patch('api.generator.generate') as mock_title:
            
            mock_summary.return_value = "Unicode摘要结果。"
            mock_title.return_value = ["Unicode标题结果"]
            
            # 测试摘要接口
            response = client.post('/summarize', 
                                 json={'text': unicode_text, 'sentences': 2})
            assert response.status_code == 200
            data = response.get_json()
            assert data['summary'] == "Unicode摘要结果。"
            
            # 测试标题接口
            response = client.post('/title', 
                                 json={'text': unicode_text, 'sentences': 1})
            assert response.status_code == 200
            data = response.get_json()
            assert data['title'] == ["Unicode标题结果"]

    @pytest.mark.integration
    def test_concurrent_requests_simulation(self, test_app):  # 使用app fixture替代client
        """模拟并发请求测试"""
        import threading
        from unittest.mock import patch

        results = []
        lock = threading.Lock()  # 创建锁用于线程安全

        def make_request():
            # 每个线程创建自己的测试客户端
            with test_app.test_client() as client:
                with patch('api.generate_summary') as mock_summary:
                    mock_summary.return_value = "并发测试结果。"
                    response = client.post(
                        '/summarize',
                        json={'text': "并发测试文本", 'sentences': 1}
                    )
                    # 使用锁保护结果添加
                    with lock:
                        results.append(response.status_code)

        # 创建并启动线程
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(results) == 3, "应收到3个响应，实际收到：{}".format(len(results))
        assert all(status == 200 for status in results), "非所有请求都成功"
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_nvidia_info_real_call(self, client):
        """测试NVIDIA信息接口的真实调用（标记为慢速测试）"""
        # 这是一个可选的真实硬件测试
        response = client.get('/nvidia_info')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'state' in data
        assert 'nvidia_version' in data
        assert 'nvidia_count' in data
        assert 'gpus' in data
        
        # 验证数据结构
        if data['state']:
            assert isinstance(data['nvidia_count'], int)
            assert isinstance(data['gpus'], list)
            assert len(data['gpus']) == data['nvidia_count']
            
            for gpu in data['gpus']:
                assert 'gpu_name' in gpu
                assert 'total' in gpu
                assert 'free' in gpu
                assert 'used' in gpu
                assert 'temperature' in gpu
                assert 'powerStatus' in gpu
