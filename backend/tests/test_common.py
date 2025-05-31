from flask import Flask
from Common import success, error, Config

class TestResp:
    """测试响应工具类"""
    
    def setup_method(self, method):
        # 每个测试方法执行前创建Flask应用实例
        self.app = Flask(__name__)

    def test_success_response(self):
        """测试成功响应格式"""
        with self.app.app_context():  # 激活应用上下文
            response = success()
            json_data = response.get_json()
            
            assert json_data["code"] == 0
            assert json_data["msg"] == "ok"
            assert json_data["body"] is None

    def test_success_with_custom_message(self):
        """测试带自定义消息的成功响应"""
        with self.app.app_context():
            custom_msg = "操作成功"
            response = success(msg=custom_msg)
            json_data = response.get_json()
            
            assert json_data["code"] == 0
            assert json_data["msg"] == custom_msg
            assert json_data["body"] is None

    def test_success_with_body(self):
        """测试带数据的成功响应"""
        with self.app.app_context():
            test_body = {"user_id": 1, "username": "test"}
            response = success(body=test_body)
            json_data = response.get_json()
            
            assert json_data["code"] == 0
            assert json_data["msg"] == "ok"
            assert json_data["body"] == test_body

    def test_error_response(self):
        """测试错误响应格式"""
        with self.app.app_context():
            response = error()
            json_data = response.get_json()
            
            assert json_data["code"] == -1
            assert json_data["msg"] == "error"
            assert json_data["body"] is None

    def test_error_with_custom_message_and_code(self):
        """测试带自定义消息和代码的错误响应"""
        with self.app.app_context():
            custom_msg = "参数错误"
            custom_code = -2
            response = error(msg=custom_msg, code=custom_code)
            json_data = response.get_json()
            
            assert json_data["code"] == custom_code
            assert json_data["msg"] == custom_msg
            assert json_data["body"] is None

    def test_error_with_body(self):
        """测试带数据的错误响应"""
        with self.app.app_context():
            test_body = {"error_detail": "缺失必要字段"}
            response = error(body=test_body)
            json_data = response.get_json()

            assert json_data["code"] == -1
            assert json_data["msg"] == "error"
            assert json_data["body"] == test_body