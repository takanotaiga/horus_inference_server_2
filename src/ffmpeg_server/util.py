from ffmpeg_server import type

def print_ffmpeg_result(code: type.FFmpegResult):
    match code:
        case type.FFmpegResult.SUCCESS:
            print("FFmpeg Success")
        case type.FFmpegResult.INPUT_NOT_FOUND:
            print("Input file not found")
        case type.FFmpegResult.OUTPUT_ALREADY:
            print("Output file already exists")
        case type.FFmpegResult.OUTPUT_NOT_WRITABLE:
            print("Output path is not writable")
        case type.FFmpegResult.FFMPEG_NOT_FOUND:
            print("FFmpeg binary not found")
        case type.FFmpegResult.TIMEOUT:
            print("FFmpeg process timed out")
        case type.FFmpegResult.FFMPEG_ERROR:
            print("FFmpeg execution error")
        case type.FFmpegResult.UNKNOWN_ERROR:
            print("An unknown error occurred")
        case _:
            print("Unrecognized result code")
