import uuid
from typing import Annotated
import os
from fastapi import FastAPI, UploadFile, File, HTTPException


app = FastAPI()

def funcWork(filepath):
    print(filepath)
    return {"class1":100,"class2":200}


@app.post("/file/upload-file")
async def upload_file(file: Annotated[UploadFile, File(description="A file must be format .mp4")],):
    if not file.filename.lower().endswith(".mp4"):
        raise HTTPException(
            status_code=400,
            detail="Only MP4 files are allowed",
        )
    id=uuid.uuid4()
    file_location = f"files/{id}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    # чота делаем...
    answer = funcWork(file_location)
    # чота делаем...
    os.remove(file_location)
    return answer
