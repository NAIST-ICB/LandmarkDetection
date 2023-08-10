#!/bin/bash

# change directory to where the bin directory exists
WS_DIR=$(realpath ${0} | xargs dirname | xargs dirname)
cd ${WS_DIR}

NUM_CPU=$(grep processor /proc/cpuinfo | wc -l)

# Configurations
IN_CT_DIR='./input'
IN_CT_FILE_EXT='mhd'
DIRECTION='AP'
OUT_DIR='./results/drr'
declare -i USE_CPU=${NUM_CPU}-1

echo NUM_CPU: ${NUM_CPU}, USE_CPU: ${USE_CPU}

export IN_CT_DIR IN_CT_FILE_EXT OUT_DIR=$(realpath ${OUT_DIR}) DIRECTION
mkdir -p ${OUT_DIR}

function main () {
  IN_CT_FILEPATH=${1}
  IN_CT_FILENAME=$(basename ${IN_CT_FILEPATH})
  OUT_DRR_FILEPATH="${OUT_DIR}/${IN_CT_FILENAME/${IN_CT_FILE_EXT}/png}"
  cmd="python src/create_drr.py \
    --in_ct_filepath ${IN_CT_FILEPATH} \
    --out_drr_filepath ${OUT_DRR_FILEPATH} \
    --direction ${DIRECTION}
  "
  echo ${cmd}
  eval ${cmd}
}
export -f main

find "$(realpath ${IN_CT_DIR})" -name "*.${IN_CT_FILE_EXT}" | \
  xargs -L 1 -I {IN_CT_FILEPATH} -P ${USE_CPU} \
    bash -c "main {IN_CT_FILEPATH}"

