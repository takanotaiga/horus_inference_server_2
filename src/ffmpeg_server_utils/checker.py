from ffmpeg_server_utils import actions
from ffmpeg_server_utils import util
from ffmpeg_server_utils.type import FFmpegResult
from horus_utils import file_control

import tempfile
import os

def a2av1_check_runner(file_path: str) -> FFmpegResult:
    with tempfile.TemporaryDirectory() as td:
        OUTPUT_FILE_PATH = os.path.join(td, "output.webm")
        result = actions.run_any_to_av1(file_path, OUTPUT_FILE_PATH)
    return result
