from ffmpeg_server_utils import type
from ffmpeg_server_utils import util
import subprocess, os
import tempfile
import re
from pathlib import Path


class FFmpegActions:
    encoder_support_list = {}

    def __init__(self):
        self.system_check()
        print("Start FFmpegActions")

    def ffmpeg_runner_action(self, command: list[str]) -> type.FFmpegResult:
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        text=True, timeout=120)
            return type.FFmpegResult.SUCCESS

        except subprocess.TimeoutExpired:
            return type.FFmpegResult.TIMEOUT

        except FileNotFoundError:
            return type.FFmpegResult.FFMPEG_NOT_FOUND

        except subprocess.CalledProcessError as e:
            print("↓====================↓")
            print(e.stderr or e.stdout)
            print("↑====================↑")
            return type.FFmpegResult.FFMPEG_ERROR

        except Exception as e:
            print("↓====================↓")
            print(e)
            print("↑====================↑")
            return type.FFmpegResult.UNKNOWN_ERROR
        
    def system_check(self):
        TEST_RESOURCE_FOLDER = "/workspace/horus_inference_server/test_resource"
        TEST_VIDEO_FILES = [
            os.path.join(TEST_RESOURCE_FOLDER, "sample_av1.mp4"),
            os.path.join(TEST_RESOURCE_FOLDER, "sample_h264.mp4"),
            os.path.join(TEST_RESOURCE_FOLDER, "sample_h265.mp4"),
            os.path.join(TEST_RESOURCE_FOLDER, "sample_mpeg2.mp4"),
            os.path.join(TEST_RESOURCE_FOLDER, "sample_mpeg4.mp4"),
            os.path.join(TEST_RESOURCE_FOLDER, "sample_vp9.mp4")
        ]

        self.encoder_support_list[type.EncoderName.AV1_NVENC] = True
        for path in TEST_VIDEO_FILES:
            with tempfile.TemporaryDirectory() as td:
                result = self.encode_backend_av1_nvenc(path, os.path.join(td, "output.mp4"))
                if result != type.FFmpegResult.SUCCESS:
                    self.encoder_support_list[type.EncoderName.AV1_NVENC] = False
                    print("NOT SUPPORT AV1 NVENC ENCODE")
                    util.print_ffmpeg_result(result)
                    break
        
        self.encoder_support_list[type.EncoderName.H264_NVENC] = True
        for path in TEST_VIDEO_FILES:
            with tempfile.TemporaryDirectory() as td:
                result = self.encode_backend_h264_nvenc(path, os.path.join(td, "output.mp4"))
                if result != type.FFmpegResult.SUCCESS:
                    self.encoder_support_list[type.EncoderName.H264_NVENC] = False
                    print("NOT SUPPORT H264 NVENC ENCODE")
                    util.print_ffmpeg_result(result)
                    break

        self.encoder_support_list[type.EncoderName.H265_NVENC] = True
        for path in TEST_VIDEO_FILES:
            with tempfile.TemporaryDirectory() as td:
                result = self.encode_backend_h265_nvenc(path, os.path.join(td, "output.mp4"))
                if result != type.FFmpegResult.SUCCESS:
                    self.encoder_support_list[type.EncoderName.H265_NVENC] = False
                    print("NOT SUPPORT H265 NVENC ENCODE")
                    util.print_ffmpeg_result(result)
                    break


    def encode(self, input_file: str, output_file: str, codec: str) -> type.FFmpegResult:
        if not os.path.isfile(input_file):
            return type.FFmpegResult.INPUT_NOT_FOUND
        if os.path.exists(output_file):
            return type.FFmpegResult.OUTPUT_ALREADY
        out_dir = os.path.dirname(output_file) or "."
        if not os.access(out_dir, os.W_OK):
            return type.FFmpegResult.OUTPUT_NOT_WRITABLE
        
        codec = re.sub(r'[^a-zA-Z0-9]', '', codec).lower()        
        match codec:
            case "av1":
                return self.encode_backend_av1_nvenc(input_file, output_file)
            case "h264":
                return self.encode_backend_av1_nvenc(input_file, output_file)
            case "h265":
                return self.encode_backend_av1_nvenc(input_file, output_file)
            case _:
                return type.FFmpegResult.UNKNOWN_ERROR

    def encode_backend_av1_nvenc(self, inp: str, out: str) -> type.FFmpegResult:
        if self.encoder_support_list[type.EncoderName.AV1_NVENC]:
            cmd = [
                "ffmpeg", "-y", "-nostdin",
                "-i", inp, "-an",
                "-c:v", "av1_nvenc", "-preset", "p1", "-tune", "ull",
                "-b:v", "3000k",
                out
            ]
            return self.ffmpeg_runner_action(cmd)
        else:
            return type.FFmpegResult.FFMPEG_ERROR
    
    def encode_backend_h264_nvenc(self, inp: str, out: str) -> type.FFmpegResult:
        if self.encoder_support_list[type.EncoderName.H264_NVENC]:
            cmd = [
                "ffmpeg", "-y", "-nostdin",
                "-i", inp, "-an",
                "-c:v", "h264_nvenc", "-preset", "p1", "-tune", "ull",
                "-b:v", "6000k",
                out
            ]
            return self.ffmpeg_runner_action(cmd)
        else:
            return type.FFmpegResult.FFMPEG_ERROR
    
    def encode_backend_h265_nvenc(self, inp: str, out: str) -> type.FFmpegResult:
        if self.encoder_support_list[type.EncoderName.H265_NVENC]:
            cmd = [
                "ffmpeg", "-y", "-nostdin",
                "-i", inp, "-an",
                "-c:v", "hevc_nvenc", "-preset", "p1", "-tune", "ull",
                "-b:v", "3000k",
                out
            ]
            return self.ffmpeg_runner_action(cmd)
        else:
            return type.FFmpegResult.FFMPEG_ERROR
