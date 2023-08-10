#!/bin/bash

export CUDA_DEVICE_ORDER='PCI_BUS_ID'
export CUDA_VISIBLE_DEVICES='0'  # '0,1'

WS_DIR=$(realpath ${0} | xargs dirname | xargs dirname)

cd ${WS_DIR}

MODEL='./yolov5/weights/only_pelvis.pt'
SOURCE='./results/drr'

SAVE_BASEDIR='./results'
SAVE_DIRNAME='yolo'

python yolov5/detect.py \
  --weights "${MODEL}" \
  --source "${SOURCE}" \
  --device "${CUDA_VISIBLE_DEVICES}" \
  --save-txt \
  --save-conf \
  --project "${SAVE_BASEDIR}" \
  --name "${SAVE_DIRNAME}"

