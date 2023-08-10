#!/usr/bin/env python3
from glob import glob
import multiprocessing as mp
import os
import sys
from typing import Optional

from tqdm import tqdm

ws_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path += [ws_dir]
from src.create_drr import main


if __name__ == '__main__':

    # Configurations
    os.chdir(ws_dir)  # change directory to where the bin directory exists
    use_cpu_num: Optional[int] = None
    in_ct_dir: str = './input'
    in_ct_file_ext: str = '.mhd'  # ex. '.mhd', '.mha', '.nii', '.nii.gz'
    direction: str = 'AP'  # 'AP' or 'LAT'
    out_dir: str = './results/drr'

    os.makedirs(out_dir, exist_ok=True)

    args_list = []
    for in_ct_filepath in glob(os.path.join(in_ct_dir, f"*{in_ct_file_ext}")):
        out_drr_filepath = os.path.join(
            out_dir,
            f"{os.path.basename(in_ct_filepath).replace(in_ct_file_ext, '.png')}"
        )
        if os.path.isfile(out_drr_filepath):
            continue
        args_list.append((
            in_ct_filepath,
            out_drr_filepath,
            direction
        ))

    def _main(args): main(*args)

    pool = mp.Pool(use_cpu_num if use_cpu_num is not None else mp.cpu_count())
    with tqdm(total=len(args_list)) as t:
        for _ in pool.imap_unordered(_main, args_list):
            t.update(1)
