# gif_recorder.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


import os

from kano.utils import ensure_dir, chown_path

from make_light.boards.router import BOARD_ROUTER
from make_light.gif.gif_encoder import GifEncoder
from make_light.paths import GIF_DIR, GIF_FILE_NAME, IMAGES_DIR
from make_light.errors import NO_FRAMES_ERROR


class GifRecorder(object):
    """
    TODO: description
    """

    def __init__(self, output_path, no_of_frames=150):
        self.output_path = output_path    # where the PNG frames are saved
        self.no_of_frames = no_of_frames  # the max number of frames to record

        # creating the output path if it doesn't exist
        ensure_dir(output_path)
        chown_path(output_path)

        self.gif_encoder = GifEncoder(output_path, GIF_DIR,
                                      delete_frames=True)

        # the gif frame list
        self.frames = list()
        # TODO: when the share image board is removed,fix TODO in _get_mask_path
        self.board_image = os.path.join(IMAGES_DIR, 'share-board-big.png')

    def reset(self):
        """
        TODO: description
        """

        self.frames = list()
        self.gif_encoder._delete_frames()  # necessary until moved into kano-gif

    def buffer_frame(self, pil_board_image):
        """
        TODO: description
        """

        if len(self.frames) < self.no_of_frames:
            self.frames.append(pil_board_image.copy())
            return True

        # reached limit, not buffering anymore
        return False

    def save_frames(self):
        """
        TODO: description
        """

        if len(self.frames) == 0:
            return NO_FRAMES_ERROR

        self._remove_leading_empty_frames()
        self._remove_trailing_empty_frames()

        # saving frames as PNGs
        for index in xrange(0, len(self.frames)):
            pixbuf = BOARD_ROUTER.board.image_to_pixbuf(self.frames[index])
            filename = os.path.join(
                self.output_path, 'frame-{0:0>3}.png'.format(index)
            )
            pixbuf.savev(filename, 'png', '', '')

        # successfully saved the frames
        return self.gif_encoder.encode_frames(GIF_FILE_NAME)

    def _remove_leading_empty_frames(self):
        # removing leading frames since the board is dark (except for one)
        # a board is 'completely dark' when all pixels are black (= 0)
        if all(pixel == 0 for pixel in list(self.frames[0].getdata())):
            found = False

            for index in xrange(1, len(self.frames)):
                frame_pixels = list(self.frames[index].getdata())
                if not all(pixel == 0 for pixel in frame_pixels):
                    found = True
                    break  # found the first non-dark frame

            if found:
                # NOTE: element [index] does not get deleted
                del self.frames[1:index]

    def _remove_trailing_empty_frames(self):
        # removing trailing frames since the board is dark (except for one)
        # a board is 'completely dark' when all pixels are black (= 0)
        if all(pixel == 0 for pixel in list(self.frames[-1].getdata())):
            found = False

            for index in xrange(len(self.frames) - 2, 0, -1):
                frame_pixels = list(self.frames[index].getdata())
                if not all(pixel == 0 for pixel in frame_pixels):
                    found = True
                    break  # found the last non-dark frame

            if found:
                # NOTE: element [-1] does not get deleted
                del self.frames[index + 1:-1]
