from core import generate_summary
from flask_cors import CORS
from flask import Flask, jsonify, request
from pynvml import *

from core import generator

app = Flask(__name__)

ALLOWED_IPS = [
    '127.0.0.1'
]


# @app.before_request
# def check_ip():
#     client_ip = request.remote_addr  # 直接获取客户端 IP
#     # 如果使用反向代理（如 Nginx），需获取 X-Forwarded-For 头
#     # client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
#
#     if client_ip not in ALLOWED_IPS:
#         return jsonify({"error": "IP 未被授权访问"}), 403


CORS_CONFIG = {
    r"/*": {
        "origins": [f"http://{ip}" for ip in ALLOWED_IPS],  # 动态生成允许来源
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["X-Custom-Header"],
        "supports_credentials": True
    }
}

CORS(app, resources=CORS_CONFIG)


@app.route('/title', methods=['POST'])
def title():
    """
    RESTful标题接口

    请求格式：
        {
            "text": "需要摘要的文本内容",
            "sentences": 可选参数，标题数（默认3）
        }

    响应格式：
        {
            "title: "生成的标题文本",
        }
    """
    try:
        # 参数验证
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing required parameter 'text'"}), 400

        text = data['text']
        sentences = int(data.get('sentences', 3))

        # 生成摘要
        title = generator.generate(text, sentences)
        result = {
            "title": title
        }
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@app.route('/summarize', methods=['POST'])
def summarize():
    """
    RESTful文本摘要接口

    请求格式：
        {
            "text": "需要摘要的文本内容",
            "sentences": 可选参数，摘要句子数（默认3）
        }

    响应格式：
        {
            "summary": "生成的摘要文本",
            "sentence_count": 实际生成的句子数
        }
    """
    try:
        if request.headers.get('Content-Type', '').lower() != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 400

        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing required parameter 'text'"}), 400

        text = data['text'].strip()
        if not text:
            return jsonify({"error": "Text cannot be empty or whitespace only"}), 400

        try:
            sentences = int(data.get('sentences', 3))
        except (TypeError, ValueError):
            return jsonify({"error": "Sentences count must be an integer"}), 400

        if sentences <= 0:
            return jsonify({"error": "Sentences count must be a positive integer"}), 400

        summary = generate_summary(text, sentences)
        return jsonify({
            "summary": summary,
            "sentence_count": len(summary)
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Summary generation failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/nvidia_info', methods=['GET'])
def nvidia_info():
    nvidia_dict = {
        "state": True,
        "nvidia_version": "",
        "nvidia_count": 0,
        "gpus": []
    }
    try:
        # 初始化NVML
        nvmlInit()
        nvidia_dict["nvidia_version"] = nvmlSystemGetDriverVersion()
        nvidia_dict["nvidia_count"] = nvmlDeviceGetCount()
        
        for i in range(nvidia_dict["nvidia_count"]):
            handle = nvmlDeviceGetHandleByIndex(i)
            memory_info = nvmlDeviceGetMemoryInfo(handle)
            
            # 显存占用率 (新增)
            memory_usage = round(memory_info.used / memory_info.total * 100, 1)
            
            # GPU计算单元利用率 (新增)
            utilization = nvmlDeviceGetUtilizationRates(handle)
            gpu_usage = utilization.gpu
            
            # 温度、功率状态等原有数据
            gpu = {
                "gpu_name": nvmlDeviceGetName(handle),
                "total": memory_info.total,
                "free": memory_info.free,
                "used": memory_info.used,
                "memory_usage_percent": memory_usage,  # 显存占用百分比
                "gpu_usage_percent": gpu_usage,        # GPU计算核心占用率
                "temperature": f"{nvmlDeviceGetTemperature(handle, 0)}℃",
                "powerStatus": nvmlDeviceGetPowerState(handle)
            }
            nvidia_dict['gpus'].append(gpu)
            
    except NVMLError as e:
        nvidia_dict["state"] = False
        # 可选：记录错误日志
        app.logger.error(f"NVML error: {str(e)}")
    except Exception as e:
        nvidia_dict["state"] = False
        # 可选：记录通用错误日志
        # app.logger.error(f"Unexpected error: {str(e)}")
    finally:
        try:
            nvmlShutdown()
        except:
            pass
    # print(nvidia_dict)
    return nvidia_dict

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
