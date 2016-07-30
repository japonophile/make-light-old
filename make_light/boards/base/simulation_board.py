# simulation_board.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Defines the abstraction of board used in the simulator

import os
from gi.repository import GdkPixbuf
from PIL import Image, ImageDraw

from kano.utils import ensure_dir, chown_path

from make_light.paths import IMAGES_DIR, TEMP_DIR
from make_light.boards.base.board import Board
from make_light.boards.base.image_helpers import load_image, get_mask_path
from make_light.boards.base.colours.colour_palette import ColourPalette


class SimulationBoard(Board):
    NAME = ''

    BOARD_IMAGE_PATH = None
    _BOARD_IMAGE = None
    _BOARD_MASK_IMAGE = None
    WELCOME_IMAGE_PATH = os.path.join(IMAGES_DIR, 'placeholders', 'welcome.gif')

    IMAGE_DIMENSIONS = (375, 375)
    _DIMENSIONS = (1, 1)

    H_OFFSET = 0
    V_OFFSET = 0

    callback = None

    def __init__(self):
        self.connected = False

        # For a full list of modes, visit:
        # pillow.readthedocs.org/en/3.0.x/handbook/concepts.html#concept-modes
        self._lights_mode = 'RGBA'

        self._board_lights_image = Image.new(
            self._lights_mode, self._DIMENSIONS
        )
        self._board_lights_draw = ImageDraw.Draw(self._board_lights_image)

        self.__class__.BOARD_IMAGE_PATH = os.path.join(
            self.__class__.BOARD_DIR, 'board.png'
        )

        debug_path = os.path.join(TEMP_DIR, 'debug')
        self._debug_filename_template = os.path.join(
            debug_path, 't{}.png'
        )
        ensure_dir(debug_path)
        chown_path(debug_path)
        self._debug = True
        self._count = 0

    @property
    def board_image(self):
        raise NotImplementedError

    def compose_image(self, im):
        return self.image_to_pixbuf(im)

    @classmethod
    def image_to_pixbuf(cls, im):
        """
        Get a GkdPixbuf of an image with the LEDs drawn on the board image.

        Args:
            im: A PIL.Image.new object containing a 14x9 pixels image with
                alpha channel. Each non transpareny pixel represents a lit
                LED on the board.
            board_image_path: The fullpath to the board image to use.

        Returns:
            A GkdPixbuf object with the LEDs drawn on the given board image.
        """
        img = cls.board_from_image(im)

        # return an image that the Gtk widget can understand
        rgb = img.convert("RGB")
        pixl = GdkPixbuf.PixbufLoader.new_with_type('pnm')

        #
        # We embed the generated image onto a PNM, Gdk compatible one
        # P6 is the magic number of PNM format, and 255 is the max color allowed
        # see: https://en.wikipedia.org/wiki/Netpbm_format
        #
        pixl.write(
            "P6 %d %d 255 " % (img.size[0], img.size[1]) + rgb.tostring()
        )
        pixbuf = pixl.get_pixbuf()
        pixl.close()

        return pixbuf


    @classmethod
    def get_board_images(cls):
        if cls._BOARD_IMAGE and cls._BOARD_MASK_IMAGE:
            return cls._BOARD_IMAGE.copy(), cls._BOARD_MASK_IMAGE.copy()

        board_image_path = cls.BOARD_IMAGE_PATH

        board_image = load_image(board_image_path)
        board_image_mask = load_image(get_mask_path(board_image_path), mode='L')

        # Pixel offsets within the board_image to reach the LED matrix

        # Right and bottom margins for the board LED matrix, in pixels
        border_margin = 35  # should be 40, to allow overflow

        # calculate how big the LEDs image has to be to fit in
        w = board_image.size[0] - cls.H_OFFSET - border_margin
        h = board_image.size[1] - cls.V_OFFSET - border_margin

        board_image_mask = board_image_mask.crop((
            cls.H_OFFSET, cls.V_OFFSET,
            cls.H_OFFSET + w, cls.V_OFFSET + h,
        ))

        cls._BOARD_IMAGE = board_image
        cls._BOARD_MASK_IMAGE = board_image_mask
        cls._LED_IMAGE_WIDTH = w
        cls._LED_IMAGE_HEIGHT = h

        return cls._BOARD_IMAGE.copy(), cls._BOARD_MASK_IMAGE.copy()


    @classmethod
    def board_from_image(cls, im):
        """
        Get a PIL.Image.new of an image with the LEDs drawn on the board image.

        Args:
            im: A PIL.Image.new object containing a 14x9 pixels image with
                alpha channel. Each non transpareny pixel represents a lit
                LED on the board.
            board_image_path: The fullpath to the board image to use.

        Returns:
            A PIL.Image.new object with the LEDs drawn on the given board image.
        """
        board_image, board_image_mask = cls.get_board_images()

        # scale up the leds image to the size of the board
        leds_layer = im.resize(
            (cls._LED_IMAGE_WIDTH, cls._LED_IMAGE_HEIGHT),
            Image.NEAREST
        )

        # If board image image load fails, display a black background LED matrix
        if not board_image:
            return leds_layer

        # Create LED luminosity alpha mask
        led_HSV_img = leds_layer.convert('HSV')
        led_brightness_mask = led_HSV_img.split()[2]

        # Clip LED luminosities to their shapes
        led_mask = Image.new('L', leds_layer.size)
        led_mask.paste(led_brightness_mask, None, mask=board_image_mask)

        # Compose coloured LEDs with their alpha masks
        board_image.paste(leds_layer, (cls.H_OFFSET, cls.V_OFFSET),
                          mask=led_mask)

        return board_image

    def _send_debug_simulation(self):
        # update method sends the next image to where it's going
        filename = self._debug_filename_template.format(self._count)
        self._count += 1
        board = self.board_from_image(
            self._board_lights_image
        )
        board.save(filename)
        chown_path(filename)

    def _send_simulation(self):
        if self.callback:
            self.callback(self._board_lights_image)

    def _update(self):
        if self._debug:
            self._send_debug_simulation()

        self._send_simulation()

    def clear(self):
        self._board_lights_draw.rectangle(
            ((0, 0), self.IMAGE_DIMENSIONS), fill=__builtins__['black']
        )

        self._update()

    def get_color(self, colour):
        print 'getting colour', colour, self.HUE
        if type(colour) == float:
            return self.get_color(int(colour * 8))

        if type(colour) == tuple:
            return colour

        if colour is True:
            intensity = 100
        elif colour is False:
            intensity = 0
        elif type(colour) == int:
            intensity = max(0, min(7, colour))

        return ColourPalette.get_colour_at_intensity(self.HUE, intensity)

    def set_callback(self, new_callback):
        SimulationBoard.callback = new_callback
