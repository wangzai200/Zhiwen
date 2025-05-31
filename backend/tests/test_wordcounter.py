"""
测试WordCounter模块
"""
import pytest
from WordCounter import getWords


class TestWordCounter:
    """测试词频统计功能"""

    def test_getwords_empty_text(self):
        """测试空文本的词频统计"""
        result = getWords("")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_getwords_short_text(self):
        """测试短文本的词频统计"""
        text = "这是一个测试文本，测试文本用于测试。"
        result = getWords(text)
        
        assert isinstance(result, list)
        # 检查结果是否为(word, count)的元组列表
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], str)
            assert isinstance(item[1], int)
        
        # 验证"测试"和"文本"在结果中
        words = [item[0] for item in result]
        assert "测试" in words
        assert "文本" in words

    def test_getwords_ignores_single_character(self):
        """测试单字符被忽略"""
        text = "一个测试"
        result = getWords(text)
        
        # 检查结果中不包含单字符
        words = [item[0] for item in result]
        assert "一" not in words
        assert "个" not in words
        assert "测试" in words

    def test_getwords_sorting(self):
        """测试结果按频率排序"""
        text = "测试文本测试文本测试测试文本测试测试"
        result = getWords(text)
        
        # 检查结果是否按频率降序排序
        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i][1] >= result[i + 1][1]

    def test_getwords_limit(self):
        """测试结果数量限制"""
        # 生成一个包含大量不同词的文本
        words = ["词" + str(i) for i in range(30)]
        text = "，".join(words)
        
        result = getWords(text)
        # 检查结果是否限制为25个
        assert len(result) <= 25
