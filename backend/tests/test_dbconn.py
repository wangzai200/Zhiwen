"""
测试Dbconn模块
"""
import pytest
import os
import sqlite3
import tempfile
import Dbconn
from Dbconn import dbGet, dbSet, init


class TestDbconn:
    """测试数据库连接和操作功能"""
    
    @pytest.fixture
    def test_db(self):
        """创建测试数据库"""
        # 创建临时数据库文件
        db_fd, db_path = tempfile.mkstemp()
        
        # 重新定向 DATABASE 全局变量到测试数据库
        original_db = Dbconn.DATABASE
        Dbconn.DATABASE = db_path
        
        # 初始化数据库连接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建测试表
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
        ''')
        conn.commit()
        conn.close()
        
        # 初始化连接
        init()
        
        yield db_path

        sqlite3.connect(db_path).close()
        # 清理
        os.close(db_fd)
        os.unlink(db_path)
        Dbconn.DATABASE = original_db
        
    def test_dbSet_insert(self, test_db):
        """测试插入操作"""
        # 执行插入操作
        result = dbSet(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ["test_name", 100]
        )
        
        # 验证返回的是行ID
        assert isinstance(result, int)
        assert result > 0
        
        # 验证数据确实被插入
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_table WHERE id = ?", [result])
        data = cursor.fetchone()
        conn.close()
        
        assert data is not None
        assert data[1] == "test_name"
        assert data[2] == 100
        
    def test_dbSet_update(self, test_db):
        """测试更新操作"""
        # 先插入一条记录
        dbSet(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ["test_name", 100]
        )
        
        # 执行更新操作
        result = dbSet(
            "UPDATE test_table SET value = ? WHERE name = ?",
            [200, "test_name"]
        )
        
        # 验证数据确实被更新
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM test_table WHERE name = ?", ["test_name"])
        data = cursor.fetchone()
        conn.close()
        
        assert data is not None
        assert data[0] == 200
        
    def test_dbGet(self, test_db):
        """测试查询操作"""
        # 插入测试数据
        dbSet(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ["test_name1", 100]
        )
        dbSet(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ["test_name2", 200]
        )
        
        # 执行查询
        result = dbGet(
            "SELECT * FROM test_table ORDER BY id",
            []
        )
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0][1] == "test_name1"
        assert result[0][2] == 100
        assert result[1][1] == "test_name2"
        assert result[1][2] == 200
        
        # 测试条件查询
        result = dbGet(
            "SELECT * FROM test_table WHERE value > ?",
            [150]
        )
        
        assert len(result) == 1
        assert result[0][1] == "test_name2"
