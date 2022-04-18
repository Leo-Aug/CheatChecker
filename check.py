import sqlite3
import os
from docx import Document
from pdfminer.high_level import extract_text
from text_compare import compare_text
from configparser import ConfigParser
from tqdm import tqdm

config = ConfigParser()
config.read('config.ini')

file_type = config['GLOBAL']['FileType']

file_dir = config[file_type]['FileDir']
database_file = config[file_type]['DatabaseFileName']


def docx_to_text(file):
    document = Document(file)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text
    return text

if file_type == 'DOCX':
    def compare_file(file1, file2):
        text1 = docx_to_text(file1)
        text2 = docx_to_text(file2)
        return compare_text(text1, text2)
elif file_type == 'PDF':
    def compare_file(file1, file2):
        text1 = extract_text(file1)
        text2 = extract_text(file2)
        return compare_text(text1, text2)


with sqlite3.connect(database_file) as con:
    cur = con.cursor()

    count = cur.execute('''
            SELECT COUNT(*) from
            (SELECT A.filename as row, B.filename as col from files as A, files as B
            EXCEPT
            SELECT row, col from matrix)
        ''').fetchall()[0][0]
    
    filepairs = [(file1, file2) for file1, file2 in cur.execute('''
            SELECT A.filename as row, B.filename as col from files as A, files as B
            EXCEPT
            SELECT row, col from matrix
        ''')]
    # 计算没有被比较过的文件
    with tqdm(total=count) as pbar:
        for file1, file2 in filepairs:
            try:
                value = compare_file(os.path.join(file_dir, file1), os.path.join(file_dir, file2))
                cur.execute('''
                    INSERT OR IGNORE INTO matrix VALUES (?, ?, ?)
                ''', (file1, file2, value))
                cur.execute('''
                    INSERT OR IGNORE INTO matrix  VALUES (?, ?, ?)
                ''', (file2, file1, value))
                
                pbar.update(2)
            except Exception as e:
                print(e)
            except KeyboardInterrupt:
                con.commit()
                break
