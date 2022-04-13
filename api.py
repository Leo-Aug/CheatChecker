from telnetlib import DO
from typing import Optional

from fastapi import FastAPI, UploadFile
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

import uvicorn

from docx import Document
from pdfminer.high_level import extract_text

from text_compare import compare_text

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


app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run(app="api:app", host="127.0.0.1", port=8000)