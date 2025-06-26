import boto3
from botocore.client import Config
from pathlib import Path

MINIO_ENDPOINT = "http://192.168.1.14:65300"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"


class S3Controller:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1"
        )
    
    def upload(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            self.s3.upload_fileobj(f, "my-bucket", Path(file_path).name)