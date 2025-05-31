"""
测试Auth模块
"""
import pytest
import jwt
import datetime
from Auth import Auth
from Common import Config


class TestAuth:
    """测试认证相关功能"""

    def test_password_hashing(self):
        """测试密码哈希功能"""
        password = "test_password"
        hashed = Auth.set_password(password)
        
        # 验证哈希密码不等于原始密码
        assert hashed != password
        
        # 验证检查密码功能
        assert Auth.check_password(hashed, password) is True
        assert Auth.check_password(hashed, "wrong_password") is False

    def test_encode_auth_token(self):
        """测试生成JWT令牌"""
        user_id = 1
        login_time = int(datetime.datetime.now().timestamp())
        token = Auth.encode_auth_token(user_id, login_time)
        
        # 验证令牌是字符串
        assert isinstance(token, str)
        
        # 验证令牌可以解码并包含正确的信息
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        assert payload["data"]["id"] == user_id
        assert payload["data"]["login_time"] == login_time

    def test_decode_auth_token(self):
        """测试解码JWT令牌"""
        user_id = 1
        login_time = int(datetime.datetime.now().timestamp())
        token = Auth.encode_auth_token(user_id, login_time)
        
        # 验证解码后的信息正确
        decoded = Auth.decode_JWT(token)
        assert decoded["data"]["id"] == user_id
        assert decoded["data"]["login_time"] == login_time

    def test_decode_invalid_token(self):
        """测试解码无效令牌"""
        with pytest.raises(Exception):
            Auth.decode_JWT("invalid_token")
