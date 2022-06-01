import json
import sqlite3
from configparser import ConfigParser, ExtendedInterpolation
from multiprocessing import shared_memory

from docx import Document
from pdfminer.high_level import extract_text
from tqdm import tqdm

from text_compare import compare_text


def check():
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

def web_check(process_shared_memory_name: str):
    json_file = "web_filelist.json"
    database_file = "webcheck_database.db"

    process_shared_memory = shared_memory.SharedMemory(name=process_shared_memory_name)
    
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
        
        pairnum = len(filepairs)
        cheak_count = 0

        # 计算没有被比较过的文件
        for file1, file2 in filepairs:
            try:
                value = compare_file(file1, file2)
                cur.execute('''
                    INSERT OR IGNORE INTO matrix VALUES (?, ?, ?)
                ''', (file1, file2, value))

                # 计算进度并存入共享内存中
                cheak_count += 1
                process = cheak_count / pairnum
                process_bits = int(process * 65535)
                buffer = process_shared_memory.buf
                buffer[1] = process_bits & 0xff
                buffer[0] = (process_bits & 0xff00) >> 8

            except Exception as e:
                print(e)
            except KeyboardInterrupt:
                con.commit()
                break

def get_check_results(file1: str, file2: str):
    with sqlite3.connect("webcheck_database.db") as con:
        cur = con.cursor()
        cur.execute('''
            SELECT * FROM matrix WHERE row = ? AND col = ?
            UNION
            SELECT * FROM matrix WHERE col = ? AND row = ?
        ''', (file1, file2, file1, file2))
        return cur.fetchone()