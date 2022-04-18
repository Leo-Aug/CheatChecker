import sqlite3
import os
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

file_type = config['GLOBAL']['FileType']

file_dir = config[file_type]['FileDir']
database_file = config[file_type]['DatabaseFileName']

with sqlite3.connect(database_file) as con:
    cur = con.cursor()

    """ 
    文件表
    filename: 文件名
    如果文件表不存在，则建表 
    """
    if not cur.execute(''' SELECT name FROM sqlite_master where name="files" ''').fetchall():
        cur.execute(
            '''CREATE TABLE files (filename TEXT PRIMARY KEY)''')

    """ 
    相似度矩阵表
    row: 行
    col: 列
    value: 相似度
    如果相似度矩阵表不存在，则建表 
    """
    if not cur.execute(''' SELECT name FROM sqlite_master where name="matrix" ''').fetchall():
        cur.execute('''CREATE TABLE matrix (
            row TEXT,
            col TEXT,
            value REAL,
            FOREIGN KEY(row) REFERENCES files(filename),
            FOREIGN KEY(col) REFERENCES files(filename)
            ) ''')

    # 将文件夹中的文件加入数据库
    for file in os.listdir(file_dir):
        cur.execute('''INSERT OR IGNORE INTO files (filename) VALUES (?)''', (file,))
