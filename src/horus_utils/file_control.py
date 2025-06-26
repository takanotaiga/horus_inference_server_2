import os
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
