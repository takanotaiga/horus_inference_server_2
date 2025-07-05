from surrealdb import Surreal
from horus_utils import file_control, s3_control
from horus_utils.type import FileType
import requests
import json
from pydantic import BaseModel
from uuid import UUID


class PreprocessStatusRequest(BaseModel):
    file_id: str
    action: str

OBJECT_STORAGE_DB_URL = "ws://database:8000/rpc"
FFMPEG_SERVER_URL = "http://horus-ffmpeg-server:8000"
CV_SERVER_URL = "http://horus-cv-server:8000"


class filePreprocesser:
    def __init__(self):
        self.object_storage_db = Surreal(OBJECT_STORAGE_DB_URL)
        self.object_storage_db.signin({"username": 'root', "password": 'root'})
        self.object_storage_db.use("dataset_collection", "object-storage-index")

        self.s3 = s3_control.S3Controller()

    def set_status(self, status: str, file_id: UUID):
        self.object_storage_db.query(
                "UPDATE preprocess_status SET status = $STATUS WHERE file_id = $FILE_ID",
                { "STATUS": status, "FILE_ID": file_id})

    def search_filepath(self, status: str) -> list[tuple[str, UUID]]:
        query_results = self.object_storage_db.query("SELECT file_id, status FROM preprocess_status WHERE status == $STATUS", {"STATUS": status})
        filepath: list[tuple[str, str]] = []
        for result in query_results:
            file_query_result = self.object_storage_db.query("SELECT raw_s3_path, file_id FROM storage_index WHERE file_id == $FILE_ID", { "FILE_ID": result["file_id"] })
            filepath.append((file_query_result[0]["raw_s3_path"], file_query_result[0]["file_id"]))

        return filepath
    
    def add_label(self):
        ready_preprocess_file = self.search_filepath("UPLOAD_COMPLETE")
        for file_path, file_id in ready_preprocess_file:
            file_type = file_control.get_file_type(file_path=file_path)
            if file_type == FileType.VIDEO:
                self.set_status("VIDEO_ENCODE_AV1_READY", file_id)

        ready_preprocess_file = self.search_filepath("VIDEO_ENCODE_AV1_COMPLETE")
        for file_path, file_id in ready_preprocess_file:
            file_type = file_control.get_file_type(file_path=file_path)
            if file_type == FileType.VIDEO:
                self.set_status("VIDEO_GENERATE_THUMBNAIL_READY", file_id)
    
    def video_av1_encode_runner(self):
        ready_preprocess_file = self.search_filepath("VIDEO_ENCODE_AV1_READY")

        for file_path, file_id in ready_preprocess_file:
            file_type = file_control.get_file_type(file_path=file_path)
            if file_type == FileType.VIDEO:
                [_, s3_share_link] = self.s3.generate_presigned_url(file_path)

                data = {
                    "fileurl": s3_share_link,
                    "codec": "av1",
                    "fileid": str(file_id)
                }

                headers = {
                    "Content-Type": "application/json"
                }

                requests.post(f"{FFMPEG_SERVER_URL}/encoder/encode_action", data=json.dumps(data), headers=headers)

                self.set_status("VIDEO_ENCODE_AV1_WIP", file_id)

    def get_chiled_file(self, file_id: UUID, hierarchy: str) -> tuple[str, UUID]:
        if type(file_id) != UUID:
            file_id = UUID(file_id)

        query_result = self.object_storage_db.query(
            "SELECT * FROM storage_index WHERE parent == $FILE_ID AND hierarchy == $HIERARCHY",
            { "FILE_ID": file_id, "HIERARCHY": hierarchy}
        )

        return query_result[0]["raw_s3_path"], query_result[0]["file_id"]


    def video_create_thumbnail_runner(self):
        ready_preprocess_file = self.search_filepath("VIDEO_GENERATE_THUMBNAIL_READY")
        
        for _, file_id in ready_preprocess_file:
            [child_path, _] = self.get_chiled_file(file_id, "encoded_video")
            file_type = file_control.get_file_type(file_path=child_path)
            if file_type == FileType.VIDEO:
                self.set_status("VIDEO_GENERATE_THUMBNAIL_WIP", file_id)
                [_, s3_share_link] = self.s3.generate_presigned_url(child_path)
                data = {
                    "fileurl": s3_share_link,
                    "fileid": str(file_id)
                }

                headers = {
                    "Content-Type": "application/json"
                }

                requests.post(f"{CV_SERVER_URL}/video/generate_thumbnail", data=json.dumps(data), headers=headers)
                self.set_status("VIDEO_GENERATE_THUMBNAIL_COMPLETE", file_id)


    def filePreprocessRunner(self):
        self.add_label()
        self.video_av1_encode_runner()
        self.video_create_thumbnail_runner()