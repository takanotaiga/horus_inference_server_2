docker build -t horus_ffmpeg_server:latest -f ./docker/Dockerfile.ffmpeg .
docker build -t horus_rtdetr_server:latest -f ./docker/Dockerfile.rtdetr .
docker build -t horus_backend_server:latest -f ./docker/Dockerfile.backend .
docker build -t horus_cv_server:latest -f ./docker/Dockerfile.opencv .

# docker run -it --rm horus_ffmpeg_server:latest
# docker run -it --rm horus_rtdetr_server:latest

# docker run \
#     -it --rm \
#     --gpus all \
#     --shm-size=32G \
#     -v ./:/workspace \
#     -v /media/taigatakano2/WD_BLACK_2T1/coco2017:/workspace/dataset \
#     horus_rtdetr_server:latest