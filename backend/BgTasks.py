import Dbconn
import Summary

import redis
from celery import Celery
from datetime import datetime

from docx import Document

import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)
app = Celery('BgTasks', 
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
)

@app.task
def test():
    print("celery ready!")


@app.task
def get_one_summary(content, max_len, filename=None, user_id=0):
    """
    获取单条摘要
    :return: 响应dict
    """
    try:
        start_time = datetime.now()

        sid = Dbconn.dbSet(
            "INSERT INTO summary_history(status, contents, words_limit, create_datetime, file_name, user_id) VALUES(?,?,?,?,?,?)",
            [0, content, max_len, datetime.strftime(start_time, "%Y-%m-%d %H:%M:%S"),
             filename, user_id]
        )

        summary = Summary.summary(content, max_len)
        title = Summary.title(content)

        summary = json.dumps(summary, ensure_ascii=False)
        title = json.dumps(title, ensure_ascii=False)

        end_time = datetime.now()
        time_use = (end_time - start_time).seconds + (end_time - start_time).microseconds / 1000000
    except:
        # 处理出错
        Dbconn.dbSet(
            "UPDATE summary_history SET status=? WHERE id=?",
            [-1, sid]
        )
    else:
        Dbconn.dbSet(
            "UPDATE summary_history SET title=?, summary=?, time_use=?, status=1 WHERE id=?",
            [title, summary, time_use, sid]
        )

        return {
            "summary": summary,
            "title": title,
            "time_use": time_use,
            "sid": sid,
        }

    return {
        "summary": "处理出错，可能字数过多",
        "title": "错误",
        "time_use": 0.0
    }


@app.task
def get_file_summary(fileName, user_id=0):
    """
    获取文件摘要
    :param fileName:
    :return:
    """
    print(fileName)
    extName = fileName.split('.')[1]
    if extName == 'txt':
        with open(fileName, 'r') as f:
            content = ""
            for line in f.readlines():
                content += line
    else:
        content = ""
        document = Document(fileName)
        for paragraph in document.paragraphs:
            content += paragraph.text

    content = content.encode('gbk', errors='ignore').decode('gbk').encode('utf-8').decode('utf-8')
    print("/".join(fileName.split('/')[1:]))
    get_one_summary.delay(content, 150, "/".join(fileName.split('/')[1:]), user_id=user_id)


if __name__ == "__main__":
    get_file_summary('upload/gortest_dcd5591/gortest/2.txt', user_id=6)
