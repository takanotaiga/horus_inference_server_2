import os, re
from horus_utils import type

def remove_file(input: str) -> type.FileRemoveResult:
    try:
        os.remove(input)
        return type.FileRemoveResult.SUCCESS
    except FileNotFoundError:
        return type.FileRemoveResult.INPUT_NOT_FOUND
    except PermissionError:
        return type.FileRemoveResult.PERMISSION_ERROR
    except Exception as e:
        return type.FileRemoveResult.UNKNOWN_ERROR
    

def get_file_type(file_path: str) -> type.FileType:
    _, file_extension = os.path.splitext(file_path)
    file_extension = re.sub(r'[^a-zA-Z]', '', file_extension).lower()

    video_extensions = [
        "mp4",
        "avi",
        "mov",
        "wmv",
        "flv",
        "webm",
        "mpg",
        "mkv",
        "asf",
        "vob"
    ]

    image_extensions = [
        "jpeg",
        "jpg",
        "png",
        "gif",
        "tiff",
        "heic"
    ]

    for ext in video_extensions:
        if ext == file_extension:
            return type.FileType.VIDEO
        
    for ext in image_extensions:
        if ext == file_extension:
            return type.FileType.VIDEO

    return type.FileType.UNKNOWN
