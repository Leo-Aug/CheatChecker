from typing import Optional

from fastapi import FastAPI

from pydantic import BaseModel

import uvicorn

from text_compare import compare_text

class TextData(BaseModel):
    text1: str
    text2: str

app = FastAPI()

@app.post("/checktext")
def check_cheat(texts: TextData):
    return compare_text(texts.text1, texts.text2)


if __name__ == "__main__":
    uvicorn.run(app="api:app", host="127.0.0.1", port=8000)