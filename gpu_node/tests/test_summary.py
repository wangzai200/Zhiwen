"""
摘要功能单元测试
测试core.summary模块
"""
import pytest
from unittest.mock import patch, Mock
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.summary import generate_summary
from .conftest import SAMPLE_TEXT, SAMPLE_SHORT_TEXT, SAMPLE_EMPTY_TEXT


class TestSummaryGeneration:
    """摘要生成测试类"""
    
    @pytest.mark.unit
    def test_generate_summary_normal_text(self):
        """测试正常文本摘要生成"""
        with patch('core.summary.jiagu.summarize') as mock_summarize:
            expected = ["这是生成的摘要文本。"]
            mock_summarize.return_value = expected

            result = generate_summary(SAMPLE_TEXT, 3)

            assert result == expected
            mock_summarize.assert_called_once_with(SAMPLE_TEXT, 3)

    @pytest.mark.unit
    def test_generate_summary_short_text(self):
        """测试短文本摘要生成"""
        with patch('core.summary.jiagu.summarize') as mock_summarize:
            expected = [SAMPLE_SHORT_TEXT]
            mock_summarize.return_value = expected

            result = generate_summary(SAMPLE_SHORT_TEXT, 1)

            assert result == expected
            mock_summarize.assert_called_once_with(SAMPLE_SHORT_TEXT, 1)

    @pytest.mark.unit
    def test_generate_summary_empty_text(self):
        """测试空文本摘要生成"""
        with pytest.raises(ValueError) as exc_info:
            generate_summary(SAMPLE_EMPTY_TEXT, 3)

        assert "Text cannot be empty" in str(exc_info.value)

    @pytest.mark.unit
    def test_generate_summary_default_sentences(self):
        """测试默认句子数参数"""
        with patch('core.summary.jiagu.summarize') as mock_summarize:
            expected = ["默认摘要。"]
            mock_summarize.return_value = expected

            result = generate_summary(SAMPLE_TEXT)

            assert result == expected
            mock_summarize.assert_called_once_with(SAMPLE_TEXT, 3)

    @pytest.mark.unit
    def test_generate_summary_custom_sentences(self):
        """测试自定义句子数参数"""
        with patch('core.summary.jiagu.summarize') as mock_summarize:
            expected = ["摘要1", "摘要2", "摘要3", "摘要4", "摘要5"]
            mock_summarize.return_value = expected

            result = generate_summary(SAMPLE_TEXT, 5)

            assert result == expected
            mock_summarize.assert_called_once_with(SAMPLE_TEXT, 5)

    @pytest.mark.unit
    def test_generate_summary_zero_sentences(self):
        """测试零句子数参数"""
        with patch('core.summary.jiagu.summarize') as mock_summarize:
            # 注意实际代码中这个参数应该被API层拦截，此处测试底层行为
            mock_summarize.return_value = []

            result = generate_summary(SAMPLE_TEXT, 0)

            assert result == ["No meaningful summary could be generated"]

    @pytest.mark.unit
    def test_generate_summary_large_sentences(self):
        """测试大句子数参数"""
        with patch('core.summary.jiagu.summarize') as mock_summarize:
            expected = ["大量句子摘要。"]
            mock_summarize.return_value = expected

            result = generate_summary(SAMPLE_TEXT, 100)

            assert result == expected
            mock_summarize.assert_called_once_with(SAMPLE_TEXT, 100)

    @pytest.mark.unit
    def test_generate_summary_jiagu_exception(self):
        """测试jiagu抛出异常的情况"""
        with patch('core.summary.jiagu.summarize') as mock_summarize:
            mock_summarize.side_effect = Exception("Jiagu processing error")

            with pytest.raises(RuntimeError) as exc_info:
                generate_summary(SAMPLE_TEXT, 3)

            assert "Summary generation failed" in str(exc_info.value)

    @pytest.mark.unit
    def test_generate_summary_unicode_text(self):
        """测试Unicode文本处理"""
        unicode_text = "这是一个包含中文、English和数字123的测试文本。emoji😀也应该被正确处理。"

        with patch('core.summary.jiagu.summarize') as mock_summarize:
            expected = ["Unicode摘要结果。"]
            mock_summarize.return_value = expected

            result = generate_summary(unicode_text, 2)

            assert result == expected
            mock_summarize.assert_called_once_with(unicode_text, 2)

    @pytest.mark.unit
    def test_generate_summary_fallback_response(self):
        """测试空结果降级处理"""
        with patch('core.summary.jiagu.summarize') as mock_summarize:
            mock_summarize.return_value = []

            result = generate_summary("有效文本", 3)

            assert result == ["No meaningful summary could be generated"]