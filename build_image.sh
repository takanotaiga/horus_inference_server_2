docker build -t horus_ffmpeg_server:latest -f ./docker/Dockerfile.ffmpeg .
docker build -t horus_rtdetr_server:latest -f ./docker/Dockerfile.rtdetr .

# docker run -it --rm horus_ffmpeg_server:latest
# docker run -it --rm horus_rtdetr_server:latest