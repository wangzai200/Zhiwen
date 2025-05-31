import pytest
import json
from unittest.mock import patch, MagicMock
from flask import url_for
from Auth import Auth


class TestAppRoutes:
    """测试应用程序API路由"""

    @patch('Auth.Auth.decode_JWT')
    def test_index_route_with_admin(self, mock_decode_jwt, client):
        """测试需要管理员权限的根路由"""
        # 模拟管理员令牌
        mock_decode_jwt.return_value = {
            'data': {
                'id': 1,
                'isAdmin': True,
                'email': 'admin@test.com',
                'username': 'admin'
            }
        }
        
        response = client.get('/', headers={
            'Authorization': 'Bearer valid_token'
        })
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['code'] == 0
        assert 'Hello World!' in data['msg']

    def test_index_route_without_auth(self, client):
        """测试无令牌访问受保护路由"""
        response = client.get('/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == -3  # 权限错误代码需要与实际一致

    @patch('Auth.Auth.encode_jwt')
    @patch('Auth.Auth.check_password')
    @patch('Dbconn.dbGet')
    def test_login_route_success(self, mock_dbget, mock_check_password, mock_encode_jwt, client):
        """测试登录路由 - 成功情况"""
        # 模拟数据库返回（email, password, id, is_admin, username）
        mock_dbget.return_value = [(
            'test@example.com', 
            'hashed_password', 
            1, 
            0,  # 非管理员
            'test_user'
        )]
        
        mock_check_password.return_value = True
        mock_encode_jwt.return_value = 'test_token'
        
        response = client.post('/user_login', json={
            'email': 'test@example.com',
            'password': 'correct_password'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert 'test_token' in data['body']['token']
        assert 'userinfo' in data['body']

    @patch('Auth.Auth.check_password')
    @patch('Dbconn.dbGet')
    def test_login_route_wrong_password(self, mock_dbget, mock_check_password, client):
        """测试登录路由 - 密码错误"""
        mock_dbget.return_value = [(
            'test@example.com', 
            'hashed_password', 
            1, 
            0, 
            'test_user'
        )]
        
        mock_check_password.return_value = False
        
        response = client.post('/user_login', json={
            'email': 'test@example.com',
            'password': 'wrong_password'
        })
        
        data = json.loads(response.data)
        assert data['code'] == -1
        assert '用户名或密码错误' in data['msg']

    @patch('Dbconn.dbGet')
    def test_login_route_user_not_found(self, mock_dbget, client):
        """测试登录路由 - 用户不存在"""
        mock_dbget.return_value = []
        
        response = client.post('/user_login', json={
            'email': 'nonexistent@test.com',
            'password': 'any_password'
        })
        
        data = json.loads(response.data)
        assert data['code'] == -1
        assert '用户未注册' in data['msg']

    class TestAppRoutes:
        """测试应用程序API路由"""

        # ... 其他测试保持不变 ...

        @patch('Auth.Auth.decode_JWT')
        def test_protected_route_with_valid_token(self, mock_decode_jwt, client):
            """测试需要登录的路由 - 有效令牌"""
            # 模拟普通用户令牌
            mock_decode_jwt.return_value = {
                'data': {
                    'id': 1,
                    'isAdmin': False,
                    'email': 'user@test.com',
                    'username': 'test_user'
                }
            }

            # 调用实际存在的需要登录的路由（例如：/get_file_summary）
            # 模拟BgTasks.get_file_summary和Dbconn.dbGet避免业务逻辑错误
            with patch('BgTasks.get_file_summary') as mock_task, \
                    patch('Dbconn.dbGet') as mock_dbget:
                mock_task.return_value = None  # 避免后台任务执行
                mock_dbget.return_value = []  # 避免数据库查询错误

                response = client.get(
                    '/get_file_summary?filename=test.txt',
                    headers={'Authorization': 'Bearer valid_token'}
                )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['code'] == 0  # 假设接口返回成功

        def test_protected_route_without_token(self, client):
            """测试需要登录的路由 - 无令牌"""
            # 调用需要登录的路由（例如：/get_file_summary）
            response = client.get('/get_file_summary?filename=test.txt')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['code'] == -3  # 对应权限错误码
            assert '登录失效' in data['msg']

        @patch('Auth.Auth.decode_JWT')
        def test_admin_route_with_non_admin_token(self, mock_decode_jwt, client):
            """测试需要管理员权限的路由 - 非管理员用户"""
            # 模拟非管理员用户访问根路由（/）
            mock_decode_jwt.return_value = {
                'data': {
                    'id': 1,
                    'isAdmin': False,  # 关键字段
                    'email': 'user@test.com',
                    'username': 'test_user'
                }
            }

            response = client.get(
                '/',
                headers={'Authorization': 'Bearer valid_token'}
            )

            data = json.loads(response.data)
            assert data['code'] == -1  # 假设管理员权限错误码为-1
            assert '无权限' in data['msg']