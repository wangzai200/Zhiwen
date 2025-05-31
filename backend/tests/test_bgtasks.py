"""
测试BgTasks模块
"""
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime
import BgTasks
import json

class TestBgTasks:
    """测试后台任务处理"""

    @patch('BgTasks.Dbconn.dbSet')
    @patch('BgTasks.Summary.title')
    @patch('BgTasks.Summary.summary')
    def test_get_one_summary(self, mock_summary, mock_title, mock_dbset):
        """测试获取单条摘要任务"""
        mock_dbset.return_value = 1  # 模拟插入后返回的ID
        mock_summary.return_value = ["摘要1", "摘要2", "摘要3"]  # 假设返回列表
        mock_title.return_value = "测试标题"

        content = "测试内容"
        max_len = 100
        filename = "test.txt"
        user_id = 1

        result = BgTasks.get_one_summary(content, max_len, filename, user_id)

        # 验证数据库插入和更新
        assert mock_dbset.call_count == 2

        insert_args = mock_dbset.call_args_list[0][0]
        assert "INSERT INTO summary_history" in insert_args[0]
        assert insert_args[1] == [0, content, max_len, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), filename, user_id]

        update_args = mock_dbset.call_args_list[1][0]
        assert "UPDATE summary_history" in update_args[0]
        expected_summary = json.dumps(mock_summary.return_value, ensure_ascii=False)
        expected_title = json.dumps(mock_title.return_value, ensure_ascii=False)
        assert update_args[1] == [expected_title, expected_summary, pytest.approx(0.0, abs=1e-3), 1]

        # 验证返回结果
        assert json.loads(result["summary"]) == mock_summary.return_value
        assert json.loads(result["title"]) == mock_title.return_value
        assert result["sid"] == 1
