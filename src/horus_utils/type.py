from enum import IntEnum, auto

class FileRemoveResult(IntEnum):
    SUCCESS = auto()
    INPUT_NOT_FOUND = auto()
    PERMISSION_ERROR = auto()
    UNKNOWN_ERROR = auto()

class FileType(IntEnum):
    VIDEO = auto()
    IMAGE = auto()
    UNKNOWN = auto()