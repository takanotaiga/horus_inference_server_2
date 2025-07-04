from backend import backend_manager

bm = backend_manager.BackendManager()

# print(bm.get_folder_list())

# print(bm.get_file_list())

# print(bm.get_preprocess_status("863d0545-55cd-48a7-aef6-7011c2de804f"))

from uuid import uuid4, UUID

# file_id = UUID("863d0545-55cd-48a7-aef6-7011c2de804f")
file_id = "863d0545-55cd-48a7-aef6-7011c2de804f"

upload_id = "YjMwYTA1OGMtNzc1NS00YTgzLTg0NWEtZDA4NGJmZGQ3N2ZkLjljYWQzZDliLTBmMDctNGRjNC04MWNlLWU3NTFhMWEwMzlmYXgxNzUxNjI3MjIzMDc1MTI0OTI1"

# print(bm.get_file_id(upload_id))

print(bm.get_preprocess_status(file_id))
print(bm.get_parent(file_id))