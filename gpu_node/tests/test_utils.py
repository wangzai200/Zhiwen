"""
测试工具和辅助函数
提供测试过程中使用的工具函数
"""
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch
import pytest


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_text(length=100, language='zh'):
        """生成指定长度和语言的测试文本"""
        if language == 'zh':
            base_text = "这是一个用于测试的中文句子。"
        elif language == 'en':
            base_text = "This is an English sentence for testing purposes."
        elif language == 'mixed':
            base_text = "这是中文 This is English 混合语言测试句子。"
        else:
            base_text = "测试文本。"
        
        # 计算需要重复的次数
        repeat_count = max(1, length // len(base_text))
        return (base_text * repeat_count)[:length]
    
    @staticmethod
    def generate_special_chars_text():
        """生成包含特殊字符的测试文本"""
        return "特殊字符!@#$%^&*()测试_+-=[]{}|;':\",./<>?~`"
    
    @staticmethod
    def generate_unicode_text():
        """生成Unicode测试文本"""
        return "Unicode测试👋🌍🚀中文English日本語العربية русский"
    
    @staticmethod
    def generate_large_text(size_mb=1):
        """生成指定大小的大文本"""
        base_text = "这是一个用于生成大文本的基础句子，用于测试系统处理大文本的能力。"
        target_size = size_mb * 1024 * 1024  # 转换为字节
        repeat_count = target_size // len(base_text.encode('utf-8'))
        return base_text * repeat_count


class MockHelper:
    """Mock辅助类"""
    
    @staticmethod
    def create_mock_tokenizer():
        """创建模拟的tokenizer"""
        mock_tokenizer = Mock()
        mock_tokenizer.tokenize.return_value = ['测', '试', '文', '本']
        mock_tokenizer.convert_tokens_to_ids.return_value = [1, 2, 3, 4]
        mock_tokenizer.convert_ids_to_tokens.return_value = ['生', '成', '结', '果']
        return mock_tokenizer
    
    @staticmethod
    def create_mock_model():
        """创建模拟的模型"""
        import torch
        
        mock_model = Mock()
        # 模拟模型输出
        mock_output = torch.randn(1, 10, 1000)  # [batch_size, seq_len, vocab_size]
        mock_model.return_value = [mock_output]
        mock_model.eval.return_value = None
        mock_model.to.return_value = mock_model
        return mock_model
    
    @staticmethod
    def create_mock_jiagu():
        """创建模拟的jiagu"""
        def mock_summarize(text, sentences):
            return f"模拟摘要: {text[:20]}... (共{sentences}句)"
        
        mock_jiagu = Mock()
        mock_jiagu.summarize.side_effect = mock_summarize
        return mock_jiagu


class FileHelper:
    """文件操作辅助类"""
    
    @staticmethod
    def create_temp_directory():
        """创建临时目录"""
        return tempfile.mkdtemp()
    
    @staticmethod
    def create_temp_file(content="", suffix=".txt"):
        """创建临时文件"""
        fd, path = tempfile.mkstemp(suffix=suffix)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
        except:
            os.close(fd)
            raise
        return path
    
    @staticmethod
    def cleanup_temp_path(path):
        """清理临时路径"""
        try:
            if os.path.isfile(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except OSError:
            pass


class AssertionHelper:
    """断言辅助类"""
    
    @staticmethod
    def assert_response_success(response, expected_keys=None):
        """断言响应成功"""
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        
        if expected_keys:
            for key in expected_keys:
                assert key in data
        
        return data
    
    @staticmethod
    def assert_response_error(response, status_code=400, error_message=None):
        """断言响应错误"""
        assert response.status_code == status_code
        data = response.get_json()
        assert 'error' in data
        
        if error_message:
            assert error_message in data['error']
        
        return data
    
    @staticmethod
    def assert_string_not_empty(value, name="value"):
        """断言字符串非空"""
        assert value is not None, f"{name} should not be None"
        assert isinstance(value, str), f"{name} should be a string"
        assert len(value.strip()) > 0, f"{name} should not be empty"
    
    @staticmethod
    def assert_valid_summary(summary, max_length=None):
        """断言有效的摘要"""
        AssertionHelper.assert_string_not_empty(summary, "summary")
        
        if max_length:
            assert len(summary) <= max_length, f"Summary too long: {len(summary)} > {max_length}"
    
    @staticmethod
    def assert_valid_title_list(titles, expected_count=None):
        """断言有效的标题列表"""
        assert isinstance(titles, list), "Titles should be a list"
        assert len(titles) > 0, "Title list should not be empty"
        
        if expected_count:
            assert len(titles) == expected_count, f"Expected {expected_count} titles, got {len(titles)}"
        
        for i, title in enumerate(titles):
            AssertionHelper.assert_string_not_empty(title, f"title[{i}]")


class PerformanceHelper:
    """性能测试辅助类"""
    
    @staticmethod
    def measure_time(func, *args, **kwargs):
        """测量函数执行时间"""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    @staticmethod
    def measure_memory(func, *args, **kwargs):
        """测量函数内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        result = func(*args, **kwargs)
        
        final_memory = process.memory_info().rss
        memory_used = final_memory - initial_memory
        
        return result, memory_used
    
    @staticmethod
    def assert_performance(execution_time, max_time, memory_used=None, max_memory=None):
        """断言性能指标"""
        assert execution_time <= max_time, f"Execution too slow: {execution_time:.3f}s > {max_time}s"
        
        if memory_used is not None and max_memory is not None:
            assert memory_used <= max_memory, f"Memory usage too high: {memory_used} > {max_memory}"


# 性能测试装饰器
def performance_test(max_time=1.0, max_memory=None):
    """性能测试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result, execution_time = PerformanceHelper.measure_time(func, *args, **kwargs)
            PerformanceHelper.assert_performance(execution_time, max_time)
            return result
        return wrapper
    return decorator


# 重试装饰器
def retry_on_failure(max_retries=3, delay=0.1):
    """失败重试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay)
            
        return wrapper
    return decorator


# 测试数据fixtures
@pytest.fixture
def sample_texts():
    """提供各种测试文本"""
    return {
        'short': "短文本测试。",
        'medium': TestDataGenerator.generate_text(500),
        'long': TestDataGenerator.generate_text(5000),
        'special': TestDataGenerator.generate_special_chars_text(),
        'unicode': TestDataGenerator.generate_unicode_text(),
        'empty': "",
        'whitespace': "   \n\t\r   ",
        'mixed_lang': TestDataGenerator.generate_text(language='mixed')
    }


@pytest.fixture
def temp_workspace():
    """提供临时工作空间"""
    temp_dir = FileHelper.create_temp_directory()
    yield temp_dir
    FileHelper.cleanup_temp_path(temp_dir)
