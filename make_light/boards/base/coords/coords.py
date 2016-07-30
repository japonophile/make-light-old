# coords.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module that defines the structure of the coordinate Class

import math
import sys

class Coords(object):

    def __init__(self):
        super(Coords, self).__init__()
        self._generate_coordinates()
        self._generate_global_helpers()

    def get_coords(self, addr):
        raise NotImplementedError

    def get_bounding_box(self, addr):
        raise NotImplementedError

    def _generate_coordinates(self):
        raise NotImplementedError

    def _generate_global_helpers(self):
        raise NotImplementedError

    @staticmethod
    def is_pos(pos):
        return type(pos) == tuple or pos == __builtins__['all']

    @staticmethod
    def polar_to_cartesian(r, theta):
        return (
            r * math.cos(math.pi * theta / 180),
            r * math.sin(math.pi * theta / 180)
        )

    @staticmethod
    def _inject_global_variables(name, val):
        builtin = sys.modules['__builtin__'].__dict__
        builtin[name] = val

    @staticmethod
    def _is_pos(pos):
        return type(pos) == tuple or pos == __builtins__['all']

    @classmethod
    def _parse_coord_args(cls, *args):
        intensity = 7
        leds = args

        # if last argument is not a coordinate, treat as a color spec
        if len(args) and not cls.is_pos(args[-1]):
            intensity = args[-1]
            leds = args[:-1]

        if len(args) and args[0] == __builtins__['all']:
            leds = [led for led in __builtins__['board']]

        return leds, intensity
