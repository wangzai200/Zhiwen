from flask import jsonify


def success(msg="ok", body=None):
    return jsonify(
        {
            'code': 0,
            'msg': msg,
            'body': body
        }
    )


def error(msg="error", body=None, code=-1):
    return jsonify(
        {
            'code': code,
            'msg': msg,
            'body': body
        }
    )


class Config:
    authcode = '142876'
    SECRET_KEY = 'a5438326-0363-463a-a058-e33d768c440b'
    APP_HOST = '127.0.0.1'
    APP_PORT = 5001
    APP_DEBUG = True

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_PASSWORD = None
    REDIS_DB = 0

    GPU_Node = {
        'GPU1': 'http://127.0.0.1:3000'
    }
