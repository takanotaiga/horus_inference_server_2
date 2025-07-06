from horus_utils import s3_control
from backend import backend_manager, file_preprocess
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
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
backend = backend_manager.BackendManager()

# uvicorn backend_api:app --host 0.0.0.0 --port 8000

@app.post("/upload/initiate")
def initiate_upload(
    filename: str = Form(...),
    folder_name:str = Form(...),
    content_type: str = Form("application/octet-stream"),
    parent: str = Form(...),
    hierarchy: str = Form(...),
): 
    [status, filepath, upload_id] = s3.get_multipart_upload_id(filename, "user-data", content_type)
    
    if status == s3_control.S3Info.SUCCESS:
        backend.uploadFileInit(
            folder=folder_name,
            filename=filename,
            upload_id=upload_id,
            s3_path=filepath,
            parent=parent,
            hierarchy=hierarchy
        )
        file_id = backend.get_file_id(upload_id)
        backend.set_status("UPLOADING", file_id)
        return {"key": filepath, "upload_id": upload_id}
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
        file_id = backend.get_file_id(upload_id)
        backend.set_status("FAILED", file_id)
        raise HTTPException(status_code=500, detail=f"upload part failed")

@app.post("/upload/complete")
def complete_upload(req: s3_control.CompleteUploadRequest):
    file_id = backend.get_file_id(req.upload_id)
    [status, resp] = s3.complete_multipart_upload(req)
    if status == s3_control.S3Info.SUCCESS:
        backend.set_status("UPLOAD_COMPLETE", file_id)

        if backend.get_parent(file_id) != "root":
            backend.set_status("COMPLETE", file_id)

        return {
            "location": resp.get("Location"),
            "bucket": resp["Bucket"],
            "key": resp["Key"],
        }
    else:
        backend.set_status("FAILED", file_id)
        raise HTTPException(status_code=500, detail=f"complete failed")

@app.post("/preprocess_status/update")
def preprocess_status_update(req: file_preprocess.PreprocessStatusRequest):
    if req.action == "FFMPEG":
        print(req.file_id)
        backend.set_status("VIDEO_ENCODE_AV1_COMPLETE", req.file_id)

@app.get("/upload/status")
def get_upload_status():
    return {"files": backend.get_file_list()}

@app.get("/storage/folder_list")
def get_folder_list():
    return {"files": backend.get_folder_list()} 

@app.get("/storage/folder_content")
def get_folder_content(folder_name: str):
    return {"files": backend.get_folder_content(folder_name)}