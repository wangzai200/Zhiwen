"""
标题生成功能单元测试
测试core.title模块
"""
import pytest
import torch
from unittest.mock import patch, Mock, MagicMock
import sys
import os
import torch.functional as F

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.title.title import TitleGenerator, _top_k_top_p_filtering
from .conftest import SAMPLE_TEXT, SAMPLE_SHORT_TEXT


class TestTopKTopPFiltering:
    """测试top-k和top-p过滤函数"""
    
    @pytest.mark.unit
    def test_top_k_filtering(self):
        """测试top-k过滤"""
        # 创建测试logits
        logits = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0],
                              [0.5, 1.5, 2.5, 3.5, 4.5]])
        
        result = _top_k_top_p_filtering(logits, top_k=3, top_p=0.0)
        
        # 检查是否只保留了top-3
        for i in range(2):  # batch_size = 2
            sorted_values, _ = torch.sort(result[i], descending=True)
            # 前3个值应该不是-inf，后面的应该是-inf
            assert not torch.isinf(sorted_values[0])
            assert not torch.isinf(sorted_values[1])
            assert not torch.isinf(sorted_values[2])
            assert torch.isinf(sorted_values[3])
            assert torch.isinf(sorted_values[4])
    
    @pytest.mark.unit
    def test_top_p_filtering(self):
        """测试top-p过滤"""
        # 创建测试logits
        logits = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0]])
        
        result = _top_k_top_p_filtering(logits, top_k=0, top_p=0.8)
        
        # 验证结果不包含无穷值（简单验证）
        assert not torch.all(torch.isinf(result))
    
    @pytest.mark.unit
    def test_no_filtering(self):
        """测试不进行过滤"""
        logits = torch.tensor([[1.0, 2.0, 3.0]])
        original_logits = logits.clone()
        
        result = _top_k_top_p_filtering(logits, top_k=0, top_p=0.0)
        
        # 结果应该与原始logits相同
        assert torch.equal(result, original_logits)
    
    @pytest.mark.unit
    def test_both_filtering(self):
        """测试同时使用top-k和top-p过滤"""
        logits = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0]])
        
        result = _top_k_top_p_filtering(logits, top_k=4, top_p=0.9)
        
        # 验证结果维度正确
        assert result.shape == logits.shape


class TestTitleGenerator:
    """标题生成器测试类"""

    @pytest.fixture
    def mock_title_generator(self):
        """创建模拟的标题生成器"""
        with patch('core.title.title.torch.cuda.is_available', return_value=False), \
                patch('core.title.title.BertTokenizer') as mock_tokenizer_class, \
                patch('core.title.title.GPT2LMHeadModel') as mock_model_class:
            # 模拟tokenizer
            mock_tokenizer = Mock()
            mock_tokenizer.tokenize.return_value = ['测', '试', '文', '本']
            # 修正convert_tokens_to_ids的处理逻辑
            mock_tokenizer.convert_tokens_to_ids.side_effect = lambda tokens: [
                {"[Content]": 1, "[Title]": 2, "[UNK]": 3, "[SEP]": 4, "[CLS]": 5}.get(token, 10)
                for token in tokens
            ]
            mock_tokenizer.convert_ids_to_tokens.return_value = ['生', '成', '标', '题']
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

            # 模拟模型
            mock_model = Mock()
            mock_model_class.from_pretrained.return_value = mock_model

            generator = TitleGenerator(
                model_path="test_model_path",
                vocab_path="test_vocab_path",
                device="cpu"
            )

            generator.tokenizer = mock_tokenizer
            generator.model = mock_model

            return generator
    
    @pytest.mark.unit
    def test_title_generator_init(self, mock_title_generator):
        """测试标题生成器初始化"""
        generator = mock_title_generator
        
        assert generator.device.type == 'cpu'
        assert generator.generate_max_len == 32
        assert generator.repetition_penalty == 1.2
        assert generator.top_k == 5
        assert generator.top_p == 0.95
        assert generator.max_len == 512
    
    @pytest.mark.unit
    def test_generate_method(self, mock_title_generator):
        """测试generate方法"""
        generator = mock_title_generator
        
        with patch.object(generator, '_predict_one_sample') as mock_predict:
            mock_predict.return_value = ["测试标题1", "测试标题2"]
            
            result = generator.generate("测试内容", 2)
            
            assert result == ["测试标题1", "测试标题2"]
            mock_predict.assert_called_once_with("测试内容", 2)
    
    @pytest.mark.unit
    @patch('core.title.title.torch.cuda.is_available')
    def test_device_selection_cuda_available(self, mock_cuda_available):
        """测试CUDA可用时的设备选择"""
        mock_cuda_available.return_value = True
        
        with patch('core.title.title.BertTokenizer'), \
             patch('core.title.title.GPT2LMHeadModel'):
            
            generator = TitleGenerator(
                model_path="test_model_path",
                vocab_path="test_vocab_path",
                device="cuda"
            )
            
            assert generator.device.type == 'cuda'
    
    @pytest.mark.unit
    @patch('core.title.title.torch.cuda.is_available')
    def test_device_selection_cuda_not_available(self, mock_cuda_available):
        """测试CUDA不可用时的设备选择"""
        mock_cuda_available.return_value = False
        
        with patch('core.title.title.BertTokenizer'), \
             patch('core.title.title.GPT2LMHeadModel'):
            
            generator = TitleGenerator(
                model_path="test_model_path",
                vocab_path="test_vocab_path",
                device="cuda"
            )
            
            assert generator.device.type == 'cpu'
    
    @pytest.mark.unit
    def test_custom_parameters(self):
        """测试自定义参数"""
        with patch('core.title.title.torch.cuda.is_available', return_value=False), \
             patch('core.title.title.BertTokenizer'), \
             patch('core.title.title.GPT2LMHeadModel'):
            
            generator = TitleGenerator(
                model_path="test_model_path",
                vocab_path="test_vocab_path",
                device="cpu",
                generate_max_len=64,
                repetition_penalty=1.5,
                top_k=10,
                top_p=0.8,
                max_len=256
            )
            
            assert generator.generate_max_len == 64
            assert generator.repetition_penalty == 1.5
            assert generator.top_k == 10
            assert generator.top_p == 0.8
            assert generator.max_len == 256
