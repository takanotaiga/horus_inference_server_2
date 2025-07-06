from horus_utils import s3_control

s3 = s3_control.S3Controller(internal_mode=False)
print(s3.generate_presigned_url("user-data/7cd47bff2b0a4054-0389eea1ba474643826192f06f583230.png"))