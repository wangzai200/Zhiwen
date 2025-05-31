import sqlite3

DATABASE = './db.sqlite'

def dbGet(sql, params):
    local_conn = sqlite3.connect(DATABASE, check_same_thread=False)
    try:
        cur = local_conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        local_conn.close()

def dbSet(sql, params):
    local_conn = sqlite3.connect(DATABASE, check_same_thread=False)
    try:
        cur = local_conn.cursor()
        cur.execute(sql, params)
        if sql.split()[0] == 'INSERT':
            ret = cur.lastrowid
        else:
            ret = cur.rowcount
        local_conn.commit()
        return ret
    finally:
        local_conn.close()

def init():
    pass  # 无需操作，仅保留接口兼容性