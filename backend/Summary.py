# coding:utf-8

import json
import requests
from Common import Config


def summary(content, max_len=3):
    # 选择GPU节点逻辑
    gpu_url = list(Config.GPU_Node.values())[0]
    req_body = {
        'text': content
    }

    resp = requests.post(url=gpu_url + "/summarize", json=req_body).text
    resp = json.loads(resp)

    summary_ret = resp['summary']

    ret = {
        'ret0': summary_ret[0],
        'ret1': summary_ret[1],
        'ret2': summary_ret[2]
    }

    return ret


def title(content):
    # 选择GPU节点逻辑
    gpu_url = list(Config.GPU_Node.values())[0]
    req_body = {
        'text': content
    }

    resp = requests.post(url=gpu_url + "/title", json=req_body).text
    resp = json.loads(resp)

    title_ret = resp['title']

    ret = {
        'ret0': title_ret[0],
        'ret1': title_ret[1],
        'ret2': title_ret[2]
    }

    return ret


if __name__ == "__main__":
    fin = open('input.txt', 'r')
    text = fin.read()
    fin.close()

    summarize = summary(text)  # 摘要
    print(summarize)
    title_ret = title(text)
    print(title_ret)
