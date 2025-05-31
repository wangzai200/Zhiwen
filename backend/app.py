from flask import Flask, request, send_from_directory
from flask_cors import CORS

import WordCounter
from Common import success, error
import Dbconn

from Common import Config
from Auth import Auth
import BgTasks

import uuid
import os
import zipfile
import functools

import json
import datetime
import psutil

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['UPLOAD_FOLDER'] = 'upload/'


def adminRequired(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        auth = request.headers.get('Authorization')
        try:
            userInfo = Auth.decode_JWT(auth)
        except:
            return error(code=-3)
        else:
            if not userInfo['data']['isAdmin']:
                return error('无权限')
            return func(*args, **kwargs)

    return inner


def loginRequired(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        auth = request.headers.get('Authorization')
        try:
            userInfo = Auth.decode_JWT(auth)
        except:
            return error(code=-3, msg="登录失效，请重新登录")
        else:
            return func(*args, **kwargs)

    return inner


@app.route('/')
@adminRequired
def hello_world():
    return success('Hello World!')


@app.route('/get_summary', methods=['POST'])
@loginRequired
def get_summary():
    content = request.form.get('content')
    max_len = int(request.form.get('max_len'))
    userInfo = Auth.decode_JWT(request.headers.get('Authorization'))['data']

    return success(body=BgTasks.get_one_summary(content, max_len, user_id=userInfo['id']))


# 上传文件
@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    filename = f.filename.split('.')[0] + '_' + str(uuid.uuid4())[0:7] + '.' + f.filename.split('.')[-1]

    extName = filename.split('.')[1]

    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return str(filename)


# 获取压缩包或单个txt文件的摘要
# @app.route('/get_file_summary')
# @loginRequired
# def get_file_summary():
#     fileName = request.args.get('filename')
#     extName = fileName.split('.')[1]
#     userInfo = Auth.decode_JWT(request.headers.get('Authorization'))['data']
#     if extName == 'zip':
#         # 处理压缩包
#         dirName = app.config['UPLOAD_FOLDER'] + fileName.split('.')[0]
#         if not os.path.exists(dirName):
#             os.makedirs(dirName)
#         zFile = zipfile.ZipFile(app.config['UPLOAD_FOLDER'] + fileName, "r")
#         for f in zFile.namelist():
#             zFile.extract(f, dirName)
#             print(dirName + '/' + f)
#             BgTasks.get_file_summary(dirName + '/' + f, user_id=userInfo['id'])
#         zFile.close()
#     elif extName == 'txt' or extName == 'docx':
#         # 处理单个txt文件
#         BgTasks.get_file_summary(app.config['UPLOAD_FOLDER'] + '/' + fileName, user_id=userInfo['id'])
#     else:
#         return error(msg="文件格式不正确")

#     return success(msg="已添加到后台处理，稍后请在'处理记录'页查看!")


# 获取压缩包或单个txt文件的摘要
@app.route('/get_file_summary')
@loginRequired
def get_file_summary():
    try:
        fileName = request.args.get('filename')
        extName = fileName.split('.')[-1]  # 使用-1更安全
        userInfo = Auth.decode_JWT(request.headers.get('Authorization'))['data']
        
        if extName == 'zip':
            # 处理压缩包
            dirName = os.path.join(app.config['UPLOAD_FOLDER'], fileName.split('.')[0])
            if not os.path.exists(dirName):
                os.makedirs(dirName)
                
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], fileName)
            print(f"处理压缩包: {zip_path}")
            
            # 解压文件
            zFile = zipfile.ZipFile(zip_path, "r")
            zFile.extractall(dirName)
            zFile.close()
            
            # 递归处理目录中的所有文件
            processed_count = 0
            for root, dirs, files in os.walk(dirName):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 只处理txt和docx文件
                    if file.endswith('.txt') or file.endswith('.docx'):
                        print(f"处理文件: {file_path}")
                        try:
                            BgTasks.get_file_summary(file_path, user_id=userInfo['id'])
                            processed_count += 1
                        except Exception as e:
                            print(f"处理文件失败: {file_path}, 错误: {str(e)}")
            
            if processed_count == 0:
                return error(msg="压缩包中没有找到可处理的文本文件")
                
        elif extName == 'txt' or extName == 'docx':
            # 处理单个txt文件
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], fileName)
            BgTasks.get_file_summary(file_path, user_id=userInfo['id'])
        else:
            return error(msg="文件格式不正确")

        return success(msg="已添加到后台处理，稍后请在'处理记录'页查看!")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error(msg=f"处理文件时出错: {str(e)}")


# 获取历史处理记录
@app.route('/get_history')
def get_history():
    ret = Dbconn.dbGet(
        """
        SELECT summary, title, time_use, file_name, create_datetime, status, summary_history.id, titleChoice, summaryChoice, user_rate.value, user_info.username, isVerify
        FROM summary_history
        LEFT JOIN user_rate
        ON summary_history.id = user_rate.sid
        LEFT JOIN user_info
        ON summary_history.user_id = user_info.id
        WHERE NOT status == -1
        """, []
    )

    ret1 = []
    for info in ret:
        info = list(info)

        if info[5] == 1:
            info[0] = json.loads(info[0])
            info[0] = info[0]['ret' + str(info[8])]

            info[1] = json.loads(info[1])
            info[1] = info[1]['ret' + str(info[7])]
        else:
            pass


        ret1.append(info)

    return success(
        body=ret1
    )


# 下载文件
@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    filename = filename.replace('\\', '/')
    return send_from_directory('./upload/', filename)


# 获取指定记录详情
@app.route('/get_detail')
def get_detail():
    id = request.args.get('id')
    ret = Dbconn.dbGet("SELECT * FROM summary_history WHERE id=?", [id])

    # 处理summary和title的dict问题
    ret = [list(ret[0])]
    ret[0][3] = json.loads(ret[0][3])
    ret[0][4] = json.loads(ret[0][4])

    return success(
        body=ret
    )


# 获取指定记录词云
@app.route('/get_cloud')
def get_cloud():
    id = request.args.get('id')

    if id == '0':
        # id为0表示查询近10条
        ret = Dbconn.dbGet("SELECT contents FROM summary_history WHERE 1=1 ORDER BY id DESC LIMIT 10 ", [])
        contents = ""
        for it in ret:
            contents += it[0]

    else:
        ret = Dbconn.dbGet("SELECT contents FROM summary_history WHERE id=?", [id])
        contents = ret[0][0]

    return success(
        body=WordCounter.getWords(contents)
    )


# 提交评价分数
@app.route('/user_rate')
def user_rate():
    sid = request.args.get('sid')
    value = request.args.get('value')

    Dbconn.dbSet("INSERT INTO user_rate(sid, value) VALUES(?,?)", [sid, value])

    return success()


# 获取评论统计
@app.route('/get_rate_statistics')
def get_rate_statistics():
    ret = Dbconn.dbGet("SELECT value, COUNT(value) from user_rate GROUP BY value;", [])

    return success(
        body=ret
    )


# 提交手动标题和摘要选择，并提交修改后内容
@app.route('/upload_choice', methods=['POST'])
def upload_choice():
    id = request.form.get('id')
    title = request.form.get('title')
    summary = request.form.get('summary')
    titleChoice = request.form.get('titleChoice')
    summaryChoice = request.form.get('summaryChoice')

    # 获取原内容
    origin = Dbconn.dbGet("SELECT * FROM summary_history WHERE id=?", [id])

    # 处理summary和title的dict问题
    origin = [list(origin[0])]
    origin[0][3] = json.loads(origin[0][3])
    origin[0][4] = json.loads(origin[0][4])

    origin[0][3]['ret' + titleChoice] = title
    origin[0][4]['ret' + summaryChoice] = summary

    try:
        ret = Dbconn.dbSet("UPDATE summary_history SET title=?, summary=?, titleChoice=?, summaryChoice=? WHERE id=?",
                           [json.dumps(origin[0][4], ensure_ascii=False), json.dumps(origin[0][3], ensure_ascii=False),
                            titleChoice, summaryChoice, id])
    except:
        return error()
    else:
        return success()


# 用户注册
@app.route('/user_register', methods=['POST'])
def user_register():
    email = request.form.get('email')
    password = request.form.get('password')
    password = Auth.set_password(password)

    auth = request.form.get('auth')
    username = request.form.get('username')

    if not auth == Config.authcode:
        return error(msg='认证码无效')

    ret = Dbconn.dbGet("SELECT email FROM user_info WHERE email=?", [email])

    if len(ret) > 0:
        return error(msg='邮箱已注册')

    Dbconn.dbSet("INSERT INTO user_info(email, password, username) VALUES(?,?,?)", [email, password, username])
    return success(msg='注册成功')


# 用户登录
@app.route('/user_login', methods=['POST'])
def user_login():
    email = request.form.get('email')
    password = request.form.get('password')

    ret = Dbconn.dbGet("SELECT email,password,id,is_admin,username FROM user_info WHERE email=?", [email])
    if not len(ret) == 1:
        return error(msg="用户未注册")

    passhash = ret[0][1]
    if not Auth.check_password(passhash, password):
        return error(msg="用户名或密码错误")

    JWT = Auth.encode_jwt(ret[0][2], ret[0][3], ret[0][0], ret[0][4])
    userinfo = {
        'userid': ret[0][2],
        'isAdmin': ret[0][3],
        'email': ret[0][0],
        'username': ret[0][4],

    }
    return success(body={
        'token': JWT,
        'userinfo': userinfo
    })


# 编辑摘要标题
@app.route('/edit_summary', methods=['POST'])
@loginRequired
def edit_summary():
    sid = request.form.get('sid')
    title_choice_id = request.form.get('title_choice_id')
    new_title = request.form.get('new_title')
    summary_choice_id = request.form.get('summary_choice_id')
    new_summary = request.form.get('new_summary')

    userInfo = Auth.decode_JWT(request.headers.get('Authorization'))['data']
    summaryInfo = Dbconn.dbGet("SELECT * FROM summary_history WHERE id=? AND user_id=?", [sid, userInfo['id']])
    if not len(summaryInfo) == 1:
        return error(msg="您无编辑权限或文章不存在")

    origin_titles = json.loads(summaryInfo[0][4])
    origin_summarys = json.loads(summaryInfo[0][3])

    origin_titles[f'ret{title_choice_id}'] = new_title
    origin_summarys[f'ret{summary_choice_id}'] = new_summary

    try:
        Dbconn.dbSet("UPDATE summary_history SET summary=?, title=?, titleChoice=?, summaryChoice=? WHERE id=?",
                     [json.dumps(origin_summarys, ensure_ascii=False), json.dumps(origin_titles, ensure_ascii=False),
                      title_choice_id, summary_choice_id, sid])
    except:
        return error(msg='编辑信息失败')
    else:
        return success()


# 管理员审核通过
@app.route('/admin_pass')
@adminRequired
def admin_pass():
    sid = request.args.get('sid')

    try:
        Dbconn.dbSet("UPDATE summary_history SET isVerify=? WHERE id=?", [1, sid])
    except:
        return error('操作失败')
    else:
        return success()


# 管理员审核拒绝
@app.route('/admin_reject')
@adminRequired
def admin_reject():
    sid = request.args.get('sid')

    try:
        Dbconn.dbSet("UPDATE summary_history SET isVerify=? WHERE id=?", [-1, sid])
    except:
        return error('操作失败')
    else:
        return success()


# 获取统计状态
@app.route('/status')
def status():
    today_datetime = datetime.datetime.now().strftime('%Y-%m-%d')
    today_sum = \
        Dbconn.dbGet(f"SELECT COUNT(*) FROM summary_history WHERE create_datetime LIKE '%%{today_datetime}%%'", [])[0][
            0]
    today_unverify = Dbconn.dbGet(
        f"SELECT COUNT(*) FROM summary_history WHERE isVerify=0", [])[
        0][0]
    info = {
        'cpu': str(psutil.cpu_percent(1)),
        'mem': str(psutil.virtual_memory().percent),
        'today_sum': today_sum,
        'today_unverify': today_unverify
    }

    return success(body=info)


if __name__ == '__main__':
    app.run(debug=Config.APP_DEBUG, host=Config.APP_HOST, port=Config.APP_PORT)
