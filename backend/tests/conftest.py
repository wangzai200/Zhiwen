"""
测试配置文件
"""
import os
import tempfile
import pytest
from app import app as flask_app


@pytest.fixture
def app():
    """创建并配置一个Flask应用实例用于测试"""
    # 设置应用为测试模式
    flask_app.config.update({
        "TESTING": True,
    })

    # 创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp()
    flask_app.config['DATABASE'] = db_path

    # 提供应用
    yield flask_app

    # 清理临时数据库
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """返回测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """返回一个测试CLI命令运行器"""
    return app.test_cli_runner()
