from surrealdb import Surreal
from uuid import uuid4, UUID
from horus_utils import state_transition, s3_control
import threading
from datetime import datetime
import time

USER_REGISTRY_DB_URL = "ws://database:8000/rpc"

class BackendManager:
    def __init__(self):
        self.object_storage_db = Surreal(USER_REGISTRY_DB_URL)
        for _ in range(5):
            try:
                self.object_storage_db.signin({"username":"root", "password":"root"})
                self.object_storage_db.use("dataset_collection", "object-storage-index")
                break
            except ConnectionRefusedError:
                time.sleep(1)
        else:
            raise RuntimeError("SurrealDB に接続できませんでした")
        
        self.s3 = s3_control.S3Controller(internal_mode=False)
        self._db_lock = threading.Lock()

    def uploadFileInit(self, folder: str, filename: str, upload_id: str, s3_path: str, parent: UUID, hierarchy: str):
        if type(parent) != UUID and parent != "root":
            parent = UUID(parent)
        file_id = uuid4()
        with self._db_lock:
            self.object_storage_db.create(
                "storage_index",
                {
                    "file_id": file_id,
                    "folder": folder,
                    "filename": filename,
                    "raw_s3_path": s3_path,
                    "parent": parent,
                    "hierarchy": hierarchy,
                    "create_time": datetime.now()
                }
            )
            self.object_storage_db.create(
                "preprocess_status",
                {
                    "file_id": file_id,
                    "status": "UNKNOWN",
                    "upload_id": upload_id,
                }
            )
    
    def set_status(self, status: str, file_id: UUID):
        if type(file_id) != UUID:
            file_id = UUID(file_id)

        old_state = self.get_preprocess_status(file_id)
        if not state_transition.state_checker(old_state, status):
            return
        with self._db_lock:
            self.object_storage_db.query(
                "UPDATE preprocess_status SET status = $PREPROCESS_STATUS WHERE file_id == $FILE_ID",
                { "PREPROCESS_STATUS": status, "FILE_ID": file_id}
            )


    def get_parent(self, file_id: UUID):
        if type(file_id) != UUID:
            file_id = UUID(file_id)

        with self._db_lock:
            query_result = self.object_storage_db.query(
                "SELECT parent FROM storage_index WHERE file_id == $FILE_ID",
                {"FILE_ID": file_id}
            )
            
        return query_result[0]["parent"]

    def get_preprocess_status(self, file_id: UUID) -> str:
        if type(file_id) != UUID:
            file_id = UUID(file_id)

        with self._db_lock:
            query_result = self.object_storage_db.query(
                "SELECT status FROM preprocess_status WHERE file_id == $FILE_ID",
                {"FILE_ID": file_id}
            )

        return query_result[0]["status"]
        
    def get_file_id(self, upload_id: str) -> UUID:
        with self._db_lock:
            query_result = self.object_storage_db.query(
                "SELECT file_id FROM preprocess_status WHERE upload_id = $UPLOAD_ID",
                {"UPLOAD_ID": upload_id}
            )
        return query_result[0]["file_id"]

    def get_file_list(self):
        with self._db_lock:
            file_list = self.object_storage_db.query("SELECT * FROM storage_index WHERE folder != '__INTERNAL_FOLDER__';")

        result = []
        for file in file_list:
            file_id = file["file_id"]
            result.append({
                "filename": file["filename"],
                "file_id": file_id,
                "folder": file["folder"],
                "status": self.get_preprocess_status(file_id),
                "create_time": file["create_time"],
            })
        return result

    def get_folder_list(self) -> list[str]:
        with self._db_lock:
            query_results = self.object_storage_db.query("SELECT folder FROM storage_index WHERE folder != '__INTERNAL_FOLDER__' GROUP BY folder;")
        folder_list: list[str] = []
        for result in query_results:
            folder_list.append(result["folder"])

        return folder_list
    
    def get_folder_content(self, folder_name: str):
        result = []
        with self._db_lock:
            folder_contents = self.object_storage_db.query(
                "SELECT file_id, filename FROM storage_index WHERE hierarchy == 'raw' AND folder == $FOLDER_NAME;",
                {"FOLDER_NAME": folder_name}
            )
            print(folder_contents)

            for content in folder_contents:
                thumbnail = self.object_storage_db.query(
                    "SELECT raw_s3_path FROM storage_index WHERE parent == $PARENT_ID AND hierarchy == 'thumbnail_image'",
                    {"PARENT_ID": content["file_id"]}
                )
                if len(thumbnail) == 0:
                    thumbnail_url = ""
                else:
                    [_, thumbnail_url] = self.s3.generate_presigned_url(thumbnail[0]["raw_s3_path"])

                result.append({
                    "filename": content["filename"],
                    "fileid": content["file_id"],
                    "thumbnail_url": thumbnail_url
                })

            return result

