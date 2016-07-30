# colour_palette.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module for abstracting colours for Make light scripts

import sys
from PIL import ImageColor

class ColourPalette(object):
    MONOCHROME = False
    HUE = None

    def __init__(self):
        self._export_named_colours()

    @staticmethod
    def get_colour_at_intensity(hue, intensity):
        saturation = 100

        if not hue:
            hue = 0
            saturation = 0

        return ImageColor.getrgb(
            'hsl({hue}, {saturation}%, {lightness}%)'
            .format(
                hue=int(hue),
                saturation=saturation,
                lightness=int(intensity)
            )
        )

    @staticmethod
    def _inject_global_variables(name, val):
        builtin = sys.modules['__builtin__'].__dict__
        builtin[name] = val

    @staticmethod
    def normalise_colour(colour):
        return tuple(channel / 255. for channel in colour)

    def _export_named_colours(self):
        mode = 'L' if self.MONOCHROME else 'RGB'

        for col, col_val in ImageColor.colormap.iteritems():
            if type(col_val) == tuple:
                col_val = 'rgb{}'.format(col_val)

            colour = ImageColor.getcolor(col_val, mode)

            if self.MONOCHROME:
                colour = self.get_colour_at_intensity(
                    self.HUE, 100 * colour / 255.
                )

            self._inject_global_variables(col, colour)

    @staticmethod
    def _parse_colour_param(colour_param):
        default_colour = __builtins__['white']

        if type(colour_param) == str:
            return ImageColor.getrgb(colour_param)

        if not (type(colour_param) == tuple or type(colour_param) == list):
            return default_colour

        normalise = max(colour_param) <= 1
        vals = []

        for channel in colour_param:
            try:
                if normalise:
                    channel *= 255.

                vals.append(int(channel))
            except (TypeError, ValueError):
                return default_colour

        return tuple(vals)

    @classmethod
    def _parse_colour_kwargs(cls, **kwargs):
        on = kwargs.get('on', True)

        if not on:
            return __builtins__['black']

        colour = __builtins__['white']

        if 'colour' in kwargs:
            colour = cls._parse_colour_param(kwargs['colour'])

        if 'color' in kwargs:
            colour = cls._parse_colour_param(kwargs['color'])

        if kwargs.get('normalise', False):
            colour = cls.normalise_colour(colour)

        return colour
