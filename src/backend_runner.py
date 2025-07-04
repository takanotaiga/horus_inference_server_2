from backend import file_preprocess
import time

fp = file_preprocess.filePreprocesser()

INTERVAL = 5  # 秒

def heavy_task():
    fp.filePreprocessRunner()

def main():
    next_time = time.time()

    while True:
        now = time.time()
        if now < next_time:
            time.sleep(next_time - now)

        start_time = time.time()
        heavy_task()
        end_time = time.time()

        next_time += INTERVAL

        if end_time - start_time > next_time:
            next_time = end_time + INTERVAL

if __name__ == "__main__":
    main()
