from horus_utils import s3_control, uuid_tools
from surrealdb import Surreal
from uuid import uuid4
import re
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
s3 = s3_control.S3Controller()

# uvicorn backend_api:app --host 0.0.0.0 --port 8000

@app.post("/upload/initiate")
def initiate_upload(
    filename: str = Form(...),
    content_type: str = Form("application/octet-stream"),
): 
    [status, filepath, id] = s3.get_multipart_upload_id(filename, "multipart", content_type)

    if status == s3_control.S3Info.SUCCESS:
        return {"key": filepath, "upload_id": id}
    else:
        raise HTTPException(status_code=500, detail=f"initiate failed")


@app.post("/upload/{upload_id}/part")
async def upload_part(
    upload_id: str,
    part_number: int = Form(...),
    key: str = Form(...),
    chunk: UploadFile = File(...),
):
    data = await chunk.read()
    [status, etag] = s3.upload_part(upload_id, part_number, key, data)

    if status == s3_control.S3Info.SUCCESS:
        return {"etag": etag}
    else:
        raise HTTPException(status_code=500, detail=f"upload part failed")


@app.post("/upload/complete")
def complete_upload(req: s3_control.CompleteUploadRequest):

    [status, resp] = s3.complete_multipart_upload(req)
    if status == s3_control.S3Info.SUCCESS:
        print(resp.get("Location"), resp["Bucket"], resp["Key"])
        return {
            "location": resp.get("Location"),
            "bucket": resp["Bucket"],
            "key": resp["Key"],
        }
    else:
        raise HTTPException(status_code=500, detail=f"complete failed")
   