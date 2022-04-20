import json
import os
import sqlite3
from configparser import ConfigParser, ExtendedInterpolation

from docx import Document
from pdfminer.high_level import extract_text
from tqdm import tqdm

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('config.ini')

file_type = config['GLOBAL']['FileType']
file_dir = config[file_type]['FileDir']
json_file = config[file_type]['JsonFileName']
database_file = config[file_type]['DatabaseFileName']

def docx_to_text(file):
    document = Document(file)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text
    return text


print("生成json文件：")
with open(json_file, 'w') as f:
    data_dir = {}
    for file in tqdm(os.listdir(file_dir)):
        if file_type == 'DOCX':
            text = docx_to_text(os.path.join(file_dir, file))
        elif file_type == 'PDF':
            text = extract_text(os.path.join(file_dir, file))
        data_dir[file] = text.replace('\n', '')
    json.dump(data_dir, f)

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
            FOREIGN KEY(col) REFERENCES files(filename),
            CONSTRAINT unique_row_col PRIMARY KEY (row, col)
            ) ''')

    # 将文件夹中的文件加入数据库
    print("将文件加入数据库：")
    for file in tqdm(os.listdir(file_dir)):
        cur.execute('''INSERT OR IGNORE INTO files (filename) VALUES (?)''', (file,))
    
    print("文件数量：", cur.execute('''SELECT COUNT(*) FROM files''').fetchone()[0])

