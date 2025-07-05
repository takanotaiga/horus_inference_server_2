from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from fastapi import FastAPI
from pydantic import BaseModel
import requests, os
from horus_utils import uuid_tools, s3_client

from cv_utils import cv_video_utils

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ThumbnailRequest(BaseModel):
    fileurl: str
    fileid: str

# uvicorn cv_api:app --host 0.0.0.0 --port 8000

@app.get("/video/meta_infomation")
def get_meta_info(fileurl: str):
    local_in = f"/tmp/{uuid_tools.get_uuid()}.mp4"

    try:
        with requests.get(fileurl, stream=True) as resp:
            resp.raise_for_status()
            with open(local_in, "wb") as f:
                for chunk in resp.iter_content(8192):
                    if chunk:
                        f.write(chunk)

        length = cv_video_utils.get_video_length_sec(local_in)
        fps = cv_video_utils.get_video_fps(local_in)
        width, height = cv_video_utils.get_video_resolution(local_in)
        codec = cv_video_utils.get_video_codec(local_in)

        if os.path.exists(local_in): os.remove(local_in)

        return {
            "length_sec": f"{length:.2f}", 
            "fps": f"{fps:.2f}",
            "resolution": {
                "width": f"{width}",
                "height": f"{height}"
            },
            "codec": codec
            }

    except requests.RequestException as e:
        print("[DownloadError]", e)
        return {"error": f"{e}"}

    except AttributeError as e:
        print("[MethodError]", e)
        return {"error": f"{e}"}

    except Exception as e:
        print("[UnknownError]", e)
        return {"error": f"{e}"}
    
@app.post("/video/generate_thumbnail")
def generate_thumbnail(req: ThumbnailRequest):
    local_in = f"/tmp/{uuid_tools.get_uuid()}.mp4"
    local_out = f"/tmp/{uuid_tools.get_uuid()}.png"

    try:
        with requests.get(req.fileurl, stream=True) as resp:
            resp.raise_for_status()
            with open(local_in, "wb") as f:
                for chunk in resp.iter_content(8192):
                    if chunk:
                        f.write(chunk)

        cv_video_utils.generate_thumbnail_at_timestamp(local_in, local_out)

        if os.path.exists(local_in): os.remove(local_in)

        s3_client.upload_file(
            file_path=local_out,
            parent=req.fileid,
            hierarchy="thumbnail_image"
        )

        return {
            "state": "complete",
            "message": "none"
            }

    except requests.RequestException as e:
        print("[DownloadError]", e)
        return {
            "state": "error",
            "message": f"{e}"
            }

    except AttributeError as e:
        print("[MethodError]", e)
        return {
            "state": "error",
            "message": f"{e}"
            }

    except Exception as e:
        print("[UnknownError]", e)
        return {
            "state": "error",
            "message": f"{e}"
            }
