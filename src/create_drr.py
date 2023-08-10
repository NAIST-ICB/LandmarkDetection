import os

import cv2
import numpy as np
import SimpleITK as sitk


MU_WATER = 0.2683
OFFSET = 900  # 800 ~ 1300
CVAL = -1000
BACK_LIMS_CT = (CVAL, 10000)  # max: 1500 -> implant remove?
VMIN_VMAX_AP = (0, 20)
VMIN_VMAX_LAT = (0, 30)


def resize(img, spacing):
    scale_percent = (spacing[2] / spacing[1]) * 100  # percent of original size
    width = img.shape[1]
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return resized


def calibrate(img):
    img[img < np.min(BACK_LIMS_CT)] = CVAL
    # img[img > np.max(BACK_LIMS_CT)] = CVAL
    # img = np.clip(img, BACK_LIMS_CT[0], BACK_LIMS_CT[1])
    img = np.maximum(np.multiply(img+1000-OFFSET, MU_WATER/1000), 0)
    return img


def generate_drr(img, direction='AP'):
    if direction == 'AP':
        axis = 1
        process = lambda x: x
    elif direction == 'LAT':
        axis = 0
        process = lambda x: np.fliplr(x)
    else:
        raise ValueError('direction must be AP or LAT')
    ret = np.sum(img, axis=axis)
    ret = ret.T
    ret = np.squeeze(ret)
    ret = process(np.flipud(ret))
    return ret


def normalize(img, vmin=None, vmax=None):
    if vmin is None or vmin < np.min(img):
        vmin = np.min(img)
    if vmax is None or vmax > np.max(img):
        vmax = np.max(img)
    return np.clip((img-vmin)/(vmax-vmin)*255.0, 0, 255).astype(np.uint8)


def read_image(filepath):
    image = sitk.ReadImage(filepath)
    array = sitk.GetArrayFromImage(image).transpose(2, 1, 0)
    spacing = image.GetSpacing()
    offset = image.GetOrigin()
    direction = image.GetDirection()

    return array, spacing, offset, direction


def main(
    in_ct_filepath: str,
    out_drr_filepath: str,
    direction: str = 'AP'
) -> None:

    img, spacing, *_ = read_image(in_ct_filepath)

    img_calib = calibrate(img)

    drr = generate_drr(img_calib, direction=direction)
    if direction == 'AP':
        vmin, vmax = VMIN_VMAX_AP
    elif direction == 'LAT':
        vmin, vmax = VMIN_VMAX_LAT
    else:
        raise ValueError('direction must be AP or LAT')

    drr = normalize(drr, vmin=vmin, vmax=vmax)
    drr = resize(drr, spacing)
    os.makedirs(os.path.dirname(out_drr_filepath), exist_ok=True)
    cv2.imwrite(out_drr_filepath, drr)


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--in_ct_filepath', type=str, required=True
    )
    parser.add_argument(
        '-o', '--out_drr_filepath', type=str, required=True
    )
    parser.add_argument(
        '-d', '--direction', type=str, default='AP', choices=('AP', 'LAT')
    )

    return parser.parse_args()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        args = parse_args()
        sys.exit(main(
            in_ct_filepath=args.in_ct_filepath,
            out_drr_filepath=args.out_drr_filepath,
            direction=args.direction,
        ))

