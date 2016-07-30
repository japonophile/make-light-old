# image_helpers.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Image helpers

import os
from PIL import Image

from kano.logging import logger

def load_image(image_path, mode=None):
    try:
        image = Image.open(image_path, 'r')
        if mode:
            image = image.convert(mode)

        return image

    except Exception as e:
        logger.error('Something unexpected occurred while computing the board'
                     ' mask path - [{}]'.format(e))
        return None  # TODO: inform the user here with UNEXPECTED_ERROR ?


def get_mask_path(image_path):
    try:
        base_path = image_path.rsplit(os.sep, 1)[0]

        mask_file_parts = os.path.basename(image_path).split('.')
        mask_file_parts[0] += '-mask'
        mask_file = '.'.join(mask_file_parts)

        # TODO: when the share image board is removed, remove this
        if mask_file.split('-', 1)[0] == 'share':
            mask_file = mask_file.split('-', 1)[1]

        return os.path.join(base_path, mask_file)

    except Exception as e:
        logger.error('Something unexpected occurred while computing the board'
                     ' mask path - [{}]'.format(e))
        return ''  # TODO: inform the user here with UNEXPECTED_ERROR ?
