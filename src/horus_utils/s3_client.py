import os
import math
import mimetypes
import requests

BACKEND_API_SERVER_URL = "http://horus-backend-api-server:8000"
CHUNK_SIZE: int = 50 * 1024 * 1024

def upload_file(
    file_path: str,
    parent: str = "root",
    hierarchy: str = "raw",
) -> dict:
    file_name = os.path.basename(file_path)
    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or "application/octet-stream"

    init_url = f"{BACKEND_API_SERVER_URL}/upload/initiate"
    init_data = {
        "filename": file_name,
        "content_type": content_type,
        "folder_name": "__INTERNAL_FOLDER__",
        "parent": parent,
        "hierarchy": hierarchy,
    }
    res = requests.post(init_url, data=init_data)
    res.raise_for_status()
    init_json = res.json()
    upload_id = init_json["upload_id"]
    key = init_json["key"]

    parts = []
    with open(file_path, "rb") as f:
        part_number = 1
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break

            part_url = f"{BACKEND_API_SERVER_URL}/upload/{upload_id}/part"
            files = {
                "chunk": (file_name, chunk, content_type),
            }
            data = {
                "upload_id": upload_id,
                "key": key,
                "part_number": str(part_number),
            }
            part_res = requests.post(part_url, data=data, files=files)
            part_res.raise_for_status()
            etag = part_res.json().get("etag")
            parts.append({"part_number": part_number, "etag": etag})
            part_number += 1

    complete_url = f"{BACKEND_API_SERVER_URL}/upload/complete"
    complete_res = requests.post(
        complete_url,
        json={"key": key, "upload_id": upload_id, "parts": parts},
    )
    complete_res.raise_for_status()
    return complete_res.json()

# upload_file("/workspace/horus_utils/s3_control.py", "ENCODED_VIDEO", "abc")