from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl
import requests, os
from ffmpeg_server import actions, type
from horus_utils import s3_control, uuid_tools

app = FastAPI()
ffmpeg_action = actions.FFmpegActions()
s3 = s3_control.S3Controller()

class EncodeRequest(BaseModel):
    fileurl: str
    codec: str
    callback_url: HttpUrl

class EncodeResponse(BaseModel):
    job_id: str

jobs: dict[str, str] = {}

def _post_result(cb_url: str, job_id: str, result: type.FFmpegResult):
    try:
        requests.post(cb_url, json={
            "job_id": job_id,
            "status": result.name,
        }, timeout=10)
    except Exception as e:
        print(f"[CallbackError] {cb_url=} {e=}")

def _encode_job(job_id: str, req: EncodeRequest):
    result = type.FFmpegResult.UNKNOWN_ERROR
    local_in = f"/tmp/{uuid_tools.get_uuid()}.mp4"
    local_out = f"/tmp/{uuid_tools.get_uuid()}.mp4"
    try:
        with requests.get(req.fileurl, stream=True) as resp:
            resp.raise_for_status()
            with open(local_in, "wb") as f:
                for chunk in resp.iter_content(8192):
                    if chunk:
                        f.write(chunk)

        result = ffmpeg_action.encode(local_in, local_out, req.codec)
        jobs[job_id] = "DONE_FFMPEG" if result == type.FFmpegResult.SUCCESS else "FAILED_RUN"

    except requests.RequestException as e:
        print("[DownloadError]", e)
        jobs[job_id] = "FAILED_DOWNLOAD"

    except AttributeError as e:
        print("[MethodError]", e)
        jobs[job_id] = "FAILED_FFMPEG_UNKNOWN"

    except Exception as e:
        print("[UnknownError]", e)
        jobs[job_id] = "FAILED_FFMPEG_UNKNOWN"
    finally:
        if os.path.exists(local_in): os.remove(local_in)

    try:
        s3.upload(local_out)
        if os.path.exists(local_out): os.remove(local_out)
        jobs[job_id] = "ALL_TASK_DONE"
    except Exception as e:
        print("[UnknownError]", e)
        jobs[job_id] = "FAILED_S3_ERROR"

@app.post("/encoder/encode_action", response_model=EncodeResponse)
def encode_action(req: EncodeRequest, background_tasks: BackgroundTasks):
    job_id = uuid_tools.get_uuid()
    jobs[job_id] = "RUNNING"
    background_tasks.add_task(_encode_job, job_id, req)
    return {"job_id": job_id}

@app.get("/encoder/job_status/{job_id}")
def job_status(job_id: str):
    status = jobs.get(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": status}

# uvicorn ffmpeg_server:app --host 0.0.0.0 --port 8000