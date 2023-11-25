import uuid
from typing import Annotated
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
import file_func
from fastapi.responses import FileResponse
from ultralytics import YOLO

app = FastAPI()


def execute(video_path, model):
    uid_name_video = file_func.time_crop_video(video_path)
    name_video, results = file_func.extract_frames_from_video(uid_name_video, model)
    return results, name_video


def funcWork(filepath):
    model_v8m_35e_6cls = YOLO('model_yolov8m_for_35e_with_two_new_class.pt')

    dicts_results, name_video_with_bb = execute(os.getcwd().replace("\\","/")+"/"+filepath, model_v8m_35e_6cls)
    # dicts_results={"ffff":11}
    # name_video_with_bb=filepath
    print(dicts_results)
    return dicts_results,name_video_with_bb


@app.get("/file/{item_id}")
def download_file(item_id: str):
  return FileResponse(path=item_id, filename=os.path.basename(item_id), media_type='multipart/form-data')

@app.post("/file/upload-file")
async def upload_file(file: Annotated[UploadFile, File(description="A file must be format .mp4")],):
    if not file.filename.lower().endswith(".mp4"):
        raise HTTPException(
            status_code=400,
            detail="Only MP4 files are allowed",
        )
    id=uuid.uuid4()
    file_location = f"files/{id}.mp4"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    # чота делаем...
    answer,bb_vid = funcWork(file_location)
    # чота делаем...
    answer['bb_vid']=bb_vid
    os.remove(file_location)
    return answer
