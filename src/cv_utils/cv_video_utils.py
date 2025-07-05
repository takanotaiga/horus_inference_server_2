import cv2
import os

def generate_thumbnail_at_timestamp(video_path: str,
                                    thumbnail_path: str) -> None:
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"動画を開けませんでした: {video_path}")

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        raise RuntimeError(f"フレーム取得に失敗しました。")

    cv2.imwrite(thumbnail_path, frame)


def get_video_length_sec(video_path: str) -> float:
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"動画を開けませんでした: {video_path}")

    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    if fps == 0:
        raise RuntimeError("FPS が取得できませんでした。")
    return frame_count / fps


def get_video_fps(video_path: str) -> float:
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"動画を開けませんでした: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    if fps <= 0:
        raise RuntimeError("FPS が取得できませんでした。")
    return fps


def get_video_resolution(video_path: str) -> tuple[int, int]:
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"動画を開けませんでした: {video_path}")

    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    return width, height


def get_video_codec(video_path: str) -> str:
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"動画を開けませんでした: {video_path}")

    fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
    cap.release()

    codec = "".join([
        chr((fourcc_int >> (8 * i)) & 0xFF)
        for i in range(4)
    ])
    return codec if codec.strip() else "UNKNOWN"