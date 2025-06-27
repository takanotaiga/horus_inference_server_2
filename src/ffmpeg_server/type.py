from enum import IntEnum, auto

class FFmpegResult(IntEnum):
    SUCCESS = auto()
    INPUT_NOT_FOUND = auto()
    OUTPUT_ALREADY = auto()
    OUTPUT_NOT_WRITABLE = auto()
    FFMPEG_NOT_FOUND = auto()
    TIMEOUT = auto()
    FFMPEG_ERROR = auto()
    UNKNOWN_ERROR = auto()

class EncoderName(IntEnum):
    AV1_NVENC = auto()
    H264_NVENC = auto()
    H264_CPU = auto()
    H265_NVENC = auto()
    H265_CPU = auto()
