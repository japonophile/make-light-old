# rectangular_board.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Implements methods for rectangular board

import os
import time
from PIL import ImageFont

from make_light.boards.base.simulation_board import SimulationBoard
from make_light.boards.base.coords.cartesian import Cartesian
from make_light.paths import FONTS_DIR


class RectangularBoard(SimulationBoard, Cartesian):
    ASPECT_RATIO = 1
    FONT = ImageFont.load(os.path.join(FONTS_DIR, 'atari-small.pil'))

    H_LED_COUNT = 0
    V_LED_COUNT = 0

    H_LED_SPACING = 0
    V_LED_SPACING = 0

    H_OFFSET = 0
    V_OFFSET = 0

    def __init__(self):
        self._DIMENSIONS = (self.H_LED_COUNT, self.V_LED_COUNT)

        SimulationBoard.__init__(self)
        Cartesian.__init__(
            self, self.H_LED_COUNT, self.V_LED_COUNT,
            self.H_LED_SPACING, self.V_LED_SPACING,
            self.H_OFFSET, self.V_OFFSET
        )

    def on(self, *args, **kwargs):
        """
        This function has several use cases:
        light.on(position)
        light.on(position...)
        light.on(position, colour=...)
        light.on(position..., colour=...)
        light.on(all)
        light.on(all, colour=...)

        when spec is not passed, it defaults to True
        When a list is passed, it is iterated over
        when 'all' is passed, we apply to all LEDs
        """
        leds, intensity = self._parse_coord_args(*args)
        fill = self._parse_colour_kwargs(**kwargs)

        if intensity != 1:
            intensity = min(intensity, 1)

            fill = self.get_colour_at_intensity(
                self.HUE, 100 * float(intensity)
            )

        for loc in leds:
            self._board_lights_draw.point(loc, fill=fill)

        self._update()

    def off(self, *args):
        if self.MONOCHROME:
            # Last argument is interpreted as intensity
            self.on(*args + (0.0,))
        else:
            self.on(*args, colour=__builtins__['black'])

    def all(self, *args, **kwargs):
        on = args[0] if args else True

        kwargs.update({'on': on})
        fill = self._parse_colour_kwargs(**kwargs)

        intensity = args[-1] if len(args) >= 2 else 7

        if intensity != 7:
            fill = self.get_colour_at_intensity(
                self.HUE, 100 * intensity / 7.
            )

        self._board_lights_draw.rectangle(((0, 0), self._DIMENSIONS), fill=fill)

        self._update()

    def rectangle(self, A, B, on=True, **kwargs):
        kwargs.update({'on': on})
        fill = self._parse_colour_kwargs(**kwargs)

        self._board_lights_draw.rectangle((A, B), fill=fill)

        self._update()

    def line(self, A, B, on=True, **kwargs):
        kwargs.update({'on': on})
        fill = self._parse_colour_kwargs(**kwargs)

        self._board_lights_draw.line((A, B), fill=fill)

        self._update()

    def circle(self, size, where, on=True, **kwargs):
        kwargs.update({'on': on})
        fill = self._parse_colour_kwargs(**kwargs)

        x, y = where

        xsize = size * (1 / self.ASPECT_RATIO)

        self._board_lights_draw.ellipse(
            (
                (x - int(xsize / 2), y - int(size / 2)),
                (x + int(xsize / 2), y + int(size / 2))
            ),
            fill
        )
        self._update()

    def ellipse(self, A, B, on=True, **kwargs):
        kwargs.update({'on': on})
        fill = self._parse_colour_kwargs(**kwargs)

        self._board_lights_draw.ellipse((A, B), fill=fill)
        self._update()

    def arc(self, middle, start, end, on=True, **kwargs):
        kwargs.update({'on': on})
        fill = self._parse_colour_kwargs(**kwargs)

        self._board_lights_draw.arc(middle, start, end, fill=fill)
        self._update()

    def triangle(self, a, b, c, on=True, **kwargs):
        kwargs.update({'on': on})
        fill = self._parse_colour_kwargs(**kwargs)

        self._board_lights_draw.polygon([a, b, c], fill=fill)
        self._update()

    def polygon(self, points, on=True, **kwargs):
        kwargs.update({'on': on})
        fill = self._parse_colour_kwargs(**kwargs)

        self._board_lights_draw.polygon(points, fill=fill)
        self._update()

    def scroll(self, text, delay=0.1, portrait=False, top=3):
        text = text + '    '
        (text_width, dummy_text_height) = self.FONT.getsize(text)
        board_width, board_height = self._DIMENSIONS
        for i in xrange(text_width):
            self._board_lights_draw.rectangle(
                (
                    (board_width - i, 0),
                    (board_width, board_height)
                ),
                fill=__builtins__['black']
            )
            self._board_lights_draw.text(
                (board_width - i, top), text, font=self.FONT,
                fill=__builtins__['white']
            )
            time.sleep(delay)
            self._update()

    def text(self, where, text):
        self._board_lights_draw.text(
            where, text, font=self.FONT, fill=__builtins__['white']
        )
        self._update()
