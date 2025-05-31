"""系统性能与压力测试"""
from collections import defaultdict

import pytest
import time
import threading
import psutil
import os
import gc
from io import BytesIO
import json
import sys

from tests.conftest import TEST_CONFIG, SAMPLE_TEXT

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app

# 生成测试数据
def generate_test_data():
    """生成不同规模的测试数据"""
    return {
        "small": "这是一个短文本。" * 10,
        "medium": SAMPLE_TEXT,
    }

class TestPerformance:
    """性能测试套件"""

    @pytest.fixture(scope="class")
    def client(self):
        """创建测试客户端"""
        app.config.update(TEST_CONFIG)
        with app.test_client() as client:
            yield client

    @pytest.mark.parametrize("payload_size,timeout", [
        ("small", 1.5),
        ("medium", 5.0),
    ])
    @pytest.mark.slow
    def test_summarize_response_time(self, client, payload_size, timeout):
        """摘要接口响应时间基准测试"""
        test_data = generate_test_data()

        # 确保测试数据存在
        if payload_size not in test_data:
            pytest.skip(f"Missing {payload_size} test data")

        # 执行测试
        start_time = time.time()
        response = client.post('/summarize', json={
            'text': test_data[payload_size],
            'sentences': 3
        })
        elapsed_time = time.time() - start_time

        # 验证结果
        assert response.status_code == 200, "接口响应失败"
        assert json.loads(response.data)['summary'], "无效的摘要结果"
        assert elapsed_time < timeout, f"响应时间超时: {elapsed_time:.2f}s > {timeout}s"

        start_time = time.time()
        response = client.post('/title', json={
            'text': test_data[payload_size],
            'sentences': 3
        })
        elapsed_time = time.time() - start_time
        assert response.status_code == 200, "标题生成接口响应失败"
        assert json.loads(response.data)['title'], "无效的标题结果"
        assert elapsed_time < timeout, f"标题生成响应时间超时: {elapsed_time:.2f}s > {timeout}s"

    @pytest.mark.slow
    def test_memory_usage_under_load(self, client):
        """持续负载下的内存稳定性测试"""
        process = psutil.Process(os.getpid())
        test_data = generate_test_data()['medium']

        # 记录初始内存
        initial_mem = process.memory_info().rss

        # 执行压力测试
        for _ in range(100):
            response = client.post('/summarize', json={
                'text': test_data,
                'sentences': 2
            })
            assert response.status_code == 200

        # 强制垃圾回收后记录内存
        gc.collect()
        final_mem = process.memory_info().rss

        # 验证内存增长在20%以内
        mem_increase = final_mem - initial_mem
        assert mem_increase < initial_mem * 0.2, "内存增长超过阈值"

class TestStress:
    """压力测试套件"""

    @pytest.fixture(scope="class")
    def client(self):
        app.config.update(TEST_CONFIG)
        with app.test_client() as client:
            yield client

    @pytest.mark.slow
    def test_concurrent_requests(self, client):
        """并发请求稳定性测试（双接口）"""
        test_data = generate_test_data()['medium']
        results = {}
        threads = []
        concurrency = 50  # 总并发数（每个接口25）

        # 定义可测试的接口列表
        endpoints = [
            ('/summarize', {'sentences': 2}),
            ('/title', {'max_length': 20})
        ]

        def worker(endpoint, params, index):
            try:
                with app.test_client() as client:
                    start = time.time()
                    # 构造动态请求参数
                    request_data = {'text': f"{test_data} - {index}"}
                    request_data.update(params)

                    response = client.post(endpoint, json=request_data)
                    results[f"{endpoint}-{index}"] = {
                        'time': time.time() - start,
                        'status': response.status_code
                    }
            except Exception as e:
                results[f"{endpoint}-{index}"] = {'error': str(e)}

        # 分配并发请求到不同接口
        for i in range(concurrency):
            endpoint, params = endpoints[i % 2]  # 轮询分配接口
            thread = threading.Thread(
                target=worker,
                args=(endpoint, params, i)
            )
            threads.append(thread)

        # 启动并等待线程
        start_time = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        total_time = time.time() - start_time

        # 结果分析（分接口统计）
        success_counter = defaultdict(int)
        failures = defaultdict(list)
        times = defaultdict(list)

        for key, res in results.items():
            endpoint = key.split('-')[0]
            status = res.get('status')
            error = res.get('error')

            if status == 200:
                success_counter[endpoint] += 1
                times[endpoint].append(res['time'])
            else:
                error_msg = f"请求 {key} 异常: {error}" if error else f"请求 {key} 状态码: {status}"
                failures[endpoint].append(error_msg)

        # 对每个接口进行断言
        for endpoint in endpoints:
            path = endpoint[0]
            total = concurrency // 2
            success = success_counter.get(path, 0)
            success_rate = success / total if total else 0

            assert success_rate >= 0.95, (
                    f"接口 {path} 成功率 {success_rate:.1%} 低于95%\n"
                    f"失败详情:\n" + "\n".join(failures.get(path, []))
            )

            # 时间统计
            if times.get(path):
                avg_time = sum(times[path]) / len(times[path])
                max_time = max(times[path])
                print(f"[{path}] 平均: {avg_time:.2f}s, 最大: {max_time:.2f}s")

        assert total_time < 15.0, f"总处理时间过长: {total_time:.2f}s"

    @pytest.mark.slow
    def test_error_handling(self, client):
        """异常输入稳定性测试"""
        test_cases = [
            ("", 400),                       # 空文本
            (None, 400),                     # 无效参数
            ({"invalid": "data"}, 400),      # 错误格式
            (BytesIO(b"binary data"), 400)   # 错误类型
        ]

        for data, expected_code in test_cases:
            response = client.post('/summarize', data=data)
            assert response.status_code == expected_code, "异常处理失败"
