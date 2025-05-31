"""
测试Summary模块
"""
import pytest
import json
import requests_mock
from Summary import summary, title
from Common import Config

class TestSummary:
    """测试文本摘要功能"""

    def test_summary_function(self):
        """测试摘要生成功能"""
        with requests_mock.Mocker() as m:  # 添加mock上下文
            # 获取配置中的GPU节点URL
            gpu_url = list(Config.GPU_Node.values())[0]
            # 构造完整的模拟请求路径
            full_url = f"{gpu_url}/summarize"
            # 正确的模拟响应数据结构
            mock_response = {
                "summary": ["测试摘要1", "测试摘要2", "测试摘要3"]
            }

            # 设置模拟POST请求到完整路径，并返回JSON响应
            m.post(full_url, json=mock_response)

            test_content = """这是一段测试文本。这段文本用于测试摘要生成功能。
            通过这个测试，我们可以验证摘要功能是否正常工作。
            希望这个测试可以成功通过。这将表明摘要功能正常。
            """

            result = summary(test_content, 100)

            # 检查返回的结构
            assert isinstance(result, dict)
            assert "ret0" in result
            assert "ret1" in result
            assert "ret2" in result

            # 验证返回的摘要与模拟数据一致
            assert result["ret0"] == "测试摘要1"
            assert result["ret1"] == "测试摘要2"
            assert result["ret2"] == "测试摘要3"

    def test_title_function(self):
        """测试标题生成功能"""
        with requests_mock.Mocker() as m:
            # 获取配置中的GPU节点URL
            gpu_url = list(Config.GPU_Node.values())[0]
            # 构造完整的模拟请求路径
            full_url = f"{gpu_url}/title"
            # 正确的模拟响应数据结构
            mock_response = {
                "title": ["测试标题1", "测试标题2", "测试标题3"]
            }

            # 设置模拟POST请求到完整路径，并返回JSON响应
            m.post(full_url, json=mock_response)

            test_content = "这是一段测试文本，用于生成标题。"
            result = title(test_content)

            # 验证返回结构和内容
            assert isinstance(result, dict)
            assert "ret0" in result
            assert result["ret0"] == "测试标题1"
            assert "ret1" in result
            assert result["ret1"] == "测试标题2"
            assert "ret2" in result
            assert result["ret2"] == "测试标题3"
