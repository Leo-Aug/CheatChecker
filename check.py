import sqlite3
from docx import Document
from pdfminer.high_level import extract_text
from text_compare import compare_text
from configparser import ConfigParser, ExtendedInterpolation
from tqdm import tqdm
import json

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('config.ini')

file_type = config['GLOBAL']['FileType']

file_dir = config[file_type]['FileDir']
json_file = config[file_type]['JsonFileName']
database_file = config[file_type]['DatabaseFileName']

with open(json_file, 'r') as f:
    data_json = json.load(f)

def compare_file(file1, file2):
    return compare_text(data_json[file1], data_json[file2])

with sqlite3.connect(database_file) as con:
    cur = con.cursor()
    
    filepairs = [(file1, file2) for file1, file2 in cur.execute('''
            SELECT A.filename as row, B.filename as col from files as A, files as B WHERE A.filename < B.filename
            EXCEPT
            SELECT row, col from matrix
        ''')]

    # 计算没有被比较过的文件
    for file1, file2 in tqdm(filepairs):
        try:
            value = compare_file(file1, file2)
            cur.execute('''
                INSERT OR IGNORE INTO matrix VALUES (?, ?, ?)
            ''', (file1, file2, value))
        except Exception as e:
            print(e)
        except KeyboardInterrupt:
            con.commit()
            break
