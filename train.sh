# CUDA_VISIBLE_DEVICES=0 torchrun \
#     --master_port=9909 \
#     --nproc_per_node=1 \
#     src/train.py \
#     -c /workspace/configs/rtdetrv2/rtdetrv2/rtdetrv2_r18vd_120e_coco.yml \
#     --use-amp \
#     --seed=0

# python src/export_onnx.py \
#     -c /workspace/configs/rtdetrv2/rtdetrv2/rtdetrv2_r18vd_120e_coco.yml \
#     -r /workspace/output/rtdetrv2_r18vd_120e_coco/best.pth \
#     --check

# python src/export_trt.py -i /workspace/model.onnx

python src/rtdetrv2_tensorrt.py -trt /workspace/model.engine -f /workspace/sample2.jpeg