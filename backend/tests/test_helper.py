"""
测试辅助工具和数据
"""
import json
import pytest
import jwt
from datetime import datetime, timedelta
from Common import Config


class TestHelper:
    """测试辅助类"""
    
    @staticmethod
    def generate_token(user_id=1, is_admin=False, expired=False):
        """
        生成测试JWT令牌
        
        Args:
            user_id: 用户ID
            is_admin: 是否为管理员
            expired: 是否生成已过期的令牌
        
        Returns:
            str: JWT令牌
        """
        # 设置过期时间
        if expired:
            exp = datetime.utcnow() - timedelta(hours=1)
        else:
            exp = datetime.utcnow() + timedelta(days=1)
        
        # 设置载荷
        login_time = int(datetime.now().timestamp())
        payload = {
            'exp': exp,
            'iat': datetime.utcnow(),
            'data': {
                'user_id': user_id,
                'login_time': login_time,
                'isAdmin': is_admin
            }
        }
        
        # 生成令牌
        token = jwt.encode(
            payload,
            Config.SECRET_KEY,
            algorithm='HS256'
        )
        
        return token
    
    @staticmethod
    def get_test_content():
        """获取测试文本内容"""
        return """这是一段用于测试的文本内容。它包含了多个句子，用于测试文本处理功能。
        这段文本应该足够长，以便能够测试摘要生成和关键词提取等功能。
        希望这个测试文本能够帮助验证程序的正确性。
        """
    
    @staticmethod
    def login(client, username="test_user", password="password"):
        """登录测试账户并获取令牌"""
        response = client.post('/user_login', json={
            'username': username,
            'password': password
        })
        data = json.loads(response.data)
        return data['body']['token'] if data['code'] == 0 else None
