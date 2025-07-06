import boto3
from botocore.client import Config
from pathlib import Path
import os
from horus_utils import uuid_tools
from enum import IntEnum, auto
from typing import Tuple, List
from pydantic import BaseModel


ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
HORUS_SEVER_BUCKET = "horus-inference-server"

class S3Info(IntEnum):
    SUCCESS = auto()
    FILE_NOT_FOUND = auto()
    UPLOAD_FAILED = auto()
    DOWNLOAD_FAILED = auto()
    DELETE_FAILED = auto()
    GET_URL_FAILED = auto()

class CompleteUploadRequest(BaseModel):
    key: str
    upload_id: str
    parts: List[dict]


class S3Controller:
    def __init__(self, internal_mode = True):
        if not internal_mode:
            MINIO_ENDPOINT = "http://dpc2500015.local:65300"
        else:
            MINIO_ENDPOINT = "http://object-storage:9000"

        self.s3 = boto3.client(
            "s3",
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1"
        )

        if not self.bucket_exists():
            print("Bucket does not exist, creating...")
            self.s3.create_bucket(Bucket=HORUS_SEVER_BUCKET)
            print("Bucket created successfully.")

    def bucket_exists(self) -> bool:
        try:
            self.s3.head_bucket(Bucket=HORUS_SEVER_BUCKET)
            return True
        except Exception as e:
            return False
    
    def file_exists(self, s3_path: str) -> S3Info:
        try:
            self.s3.head_object(Bucket=HORUS_SEVER_BUCKET, Key=s3_path)
            return S3Info.SUCCESS
        except Exception as e:
            return S3Info.FILE_NOT_FOUND

    def upload(self, file_path: str, save_folder: str) -> Tuple[S3Info, str]:
        save_path = os.path.join(save_folder, uuid_tools.get_uuid(16) + "-" + Path(file_path).name)
        try:
            with open(file_path, "rb") as f:
                self.s3.upload_fileobj(f, HORUS_SEVER_BUCKET, save_path)
            return S3Info.SUCCESS, save_path
        except Exception as e:
            return S3Info.UPLOAD_FAILED, "Upload failed: " + str(e)
        
    def get_multipart_upload_id(self, file_path: str, save_folder: str, content_type: str) -> Tuple[S3Info, str, str]:
        save_path = os.path.join(save_folder, uuid_tools.get_uuid(16) + "-" + Path(file_path).name)
        try:
           resp = self.s3.create_multipart_upload(
                Bucket=HORUS_SEVER_BUCKET,
                Key=save_path,
                ContentType=content_type,
            )
           return S3Info.SUCCESS, save_path, resp["UploadId"]
        except Exception as e:
            print(e)
            return S3Info.UPLOAD_FAILED, "", ""

    def upload_part(self, upload_id: str, part_number: int, key: str, data: bytes) -> Tuple[S3Info, str]:
        try:
            resp = self.s3.upload_part(
                    Bucket=HORUS_SEVER_BUCKET,
                    Key=key,
                    UploadId=upload_id,
                    PartNumber=part_number,
                    Body=data,
                )
            return S3Info.SUCCESS, resp["ETag"]
        except Exception as e:
            print(e)
            return S3Info.UPLOAD_FAILED, ""
        
    def complete_multipart_upload(self, req: CompleteUploadRequest):
        try:
            parts = [
                {"PartNumber": p["part_number"], "ETag": p["etag"]}
                for p in req.parts
            ]
            resp = self.s3.complete_multipart_upload(
                Bucket=HORUS_SEVER_BUCKET,
                Key=req.key,
                UploadId=req.upload_id,
                MultipartUpload={"Parts": parts},
            )
            return S3Info.SUCCESS, resp
        except Exception as e:
            print(e)
            return S3Info.UPLOAD_FAILED, e

    def download(self, s3_path: str) -> Tuple[S3Info, str]:
        save_path = os.path.join("/tmp", Path(s3_path).name)
        try:
            with open(save_path, "wb") as f:
                self.s3.download_fileobj(HORUS_SEVER_BUCKET, s3_path, f)
            return S3Info.SUCCESS, save_path
        except Exception as e:
            return S3Info.DOWNLOAD_FAILED, "Download failed: " + str(e)
        
    def delete(self, s3_path: str) -> S3Info:
        if self.file_exists(s3_path) != S3Info.SUCCESS:
            return S3Info.FILE_NOT_FOUND
        try:
            self.s3.delete_object(Bucket=HORUS_SEVER_BUCKET, Key=s3_path)
            return S3Info.SUCCESS
        except Exception as e:
            return S3Info.DELETE_FAILED
        
    def generate_presigned_url(self, s3_path: str, expiration_sec: int = 3600) -> Tuple[S3Info, str]:
        try:
            url = self.s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': HORUS_SEVER_BUCKET,
                    'Key': s3_path
                },
                ExpiresIn=expiration_sec
            )
            return S3Info.SUCCESS, url
        except Exception as e:
            return S3Info.GET_URL_FAILED, f"Failed to generate presigned URL: {e}"

