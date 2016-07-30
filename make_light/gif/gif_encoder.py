# gif_encoder.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


import os

from kano.utils import ensure_dir, chown_path

from make_light.errors import NO_FRAMES_ERROR, SIZE_REQ_ERROR, UNEXPECTED_ERROR


class GifEncoder(object):
    """
    TODO: description

    For why FPS is set to 5, read the link below, page 14
    http://stakeholders.ofcom.org.uk/binaries/broadcast/guidance/831193/section2.pdf
    """

    ENCODING_TRIES = 5

    def __init__(self, input_path, output_path,
                 fps=5, repeating=True, max_size=500, delete_frames=False):
        self.input_path = input_path    # where all the PNGs for the GIF are
        self.output_path = output_path  # path to the resulting GIF

        self.fps = fps                  # GIFs frames per second animation
        self.repeating = repeating      # whether the GIF continuously loops
        self.max_size = max_size        # resulting GIF max size (kB)
        self.delete_frames = delete_frames  # delete frames after encoding

        # creating paths if they doesn't exist
        ensure_dir(input_path)
        chown_path(input_path)
        ensure_dir(output_path)
        chown_path(output_path)

    def encode_frames(self, name, resize_width=None, resize_height=None):
        '''
        TODO: description
        '''

        gif_path = os.path.join(self.output_path, name)

        # list with fullpaths of all frames
        frames = self._get_frames_fullpath()
        if len(frames) == 0:
            # TODO: logger.warn 'oops, no frames'
            return NO_FRAMES_ERROR

        # ImageMagick args
        fps_arg = '-delay 1x{}'.format(self.fps)
        repeat_arg = '-loop {}'.format(0 if self.repeating else 1)
        resize_arg = '-resize {}x{}'.format(resize_width, resize_height) if (
            resize_width and resize_height
        ) else ''

        # encode the GIF using progressively less frames until the
        # size requirement is met (eliminate frames from the end)
        for i in xrange(self.ENCODING_TRIES):
            last_index = len(frames) - (i * len(frames) / self.ENCODING_TRIES)
            frames_path = ' '.join(frames[0:last_index])

            cmd = 'convert {args} -layers optimize {frames_path} {gif_path}'.format(
                args=fps_arg + ' ' + repeat_arg + ' ' + resize_arg,
                frames_path=frames_path,
                gif_path=gif_path
            )
            # call ImageMagick to work it's GIF making magic
            # debugger('GifEncoder: encode_frames: cmd is {}'.format(cmd))
            os.system(cmd)

            # add a delay to the end of the GIF when it repeats
            if self.repeating:
                cmd = 'convert {} \( +clone -set delay 300 \) +swap +delete {}'.format(
                    gif_path,
                    gif_path
                )
                os.system(cmd)

            # take more frames off the end if GIF is too big
            try:
                gif_size = os.path.getsize(gif_path) / 1024.0  # kB

                if gif_size < self.max_size:
                    self._delete_frames()
                    return dict()  # success - return empty error

            except:
                # TODO: logger warn here, ImageMagick failed
                return UNEXPECTED_ERROR

        # TODO: logger.info 'could not encode the GIF to match the size req'
        return SIZE_REQ_ERROR

    def _get_frames_fullpath(self):
        frames = list()
        # making sure we always only process PNGs for GIF frames
        for frame in sorted(os.listdir(self.input_path)):
            if frame.endswith('.png'):
                frames.append(os.path.join(self.input_path, frame))
        return frames

    def _delete_frames(self):
        if not self.delete_frames:
            return

        for frame in os.listdir(self.input_path):
            frame_path = os.path.join(self.input_path, frame)
            try:
                if os.path.isfile(frame_path) and frame_path.endswith('.png'):
                    os.unlink(frame_path)
            except Exception as e:
                # TODO: logger here
                pass

    def resize_gif(self, name, resize_width, resize_height):
        """
        TODO: description
        """

        # TODO: check for input/output_gif, width, height
        # TODO: think about the name being a param

        cmd = 'convert {input_gif} -coalesce - | ' \
              'convert - -resize {width}x{height} -layers optimize {output_gif}'.format(
                  width=resize_width,
                  height=resize_height,
                  input_gif=os.path.join(self.output_path, name),
                  output_gif=os.path.join(self.output_path, name)
              )
        # call ImageMagick to work it's gif making magic
        os.system(cmd)
