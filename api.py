from multiprocessing import shared_memory, Process
from telnetlib import DO
from typing import List, Optional

import uvicorn
from docx import Document
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from pdfminer.high_level import extract_text
from pydantic import BaseModel

from databaseini import init_web_system
from text_compare import compare_text
from check import web_check, get_check_results

files = {}
result_readable = True
shm_a = shared_memory.SharedMemory(create=True, size=2)

class TextData(BaseModel):
    text1: str
    text2: str

app = FastAPI()

@app.post("/checktext")
def check_cheat(texts: TextData):
    return compare_text(texts.text1, texts.text2)

def parse_text(file: UploadFile) -> Optional[str]:
    """
    从不同的文件中解析文本
    """
    if(file.filename.endswith(".docx")):
        document = Document(file.file._file)
        text = ""
        for paragraph in document.paragraphs:
            text += paragraph.text
        return text
    elif(file.filename.endswith(".pdf")):
        text = extract_text(file.file._file)
        return text

@app.post("/checkfile")
def check_cheat(file1: UploadFile, file2: UploadFile):
    """
    比较两个文件的相似度
    """
    return compare_text(parse_text(file1), parse_text(file2))

@app.post("/receivefile")
def receive_file(filelist: List[UploadFile] = File(...)):
    for file in filelist:
        files[file.filename] = parse_text(file)
    return True

@app.get("/files")
def get_files():
    return list(files.keys())

@app.get("/startcheck")
def start_check():
    result_readable = False
    init_web_system(files)
    p = Process(target=web_check, args=(shm_a.name,))
    p.start()
    return "started"

@app.get("/getprocess")
def get_process():
    # 读取共享内存的值
    buffer = shm_a.buf
    return ((buffer[0] << 8) | buffer[1]) / 65535

@app.get("/getresult")
def get_result(file1: str, file2: str):
    return get_check_results(file1, file2)



app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run(app="api:app", host="0.0.0.0", port=80)
