# cartesian.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Implements methods for cartesian coordinates

import itertools

from make_light.boards.base.coords.coords import Coords


class Cartesian(Coords):

    def __init__(self, h_led_count, v_led_count, h_led_spacing=0,
                 v_led_spacing=0, h_offset=0, v_offset=0):
        self._h_led_count = h_led_count
        self._v_led_count = v_led_count

        self._h_led_spacing = h_led_spacing
        self._v_led_spacing = v_led_spacing

        self._h_offset = h_offset
        self._v_offset = v_offset

        super(Cartesian, self).__init__()

    def get_coords(self, addr):
        h_led_idx, v_led_idx = addr
        return (
            self._h_led_spacing * h_led_idx + self._h_offset,
            self._v_led_spacing * v_led_idx + self._v_offset,
        )

    def get_bounding_box(self, addr):
        x, y = self.get_coords(addr)
        h_range = self._h_led_spacing / 2
        v_range = self._v_led_spacing / 2

        return {
            'top-left': (
                x - h_range,
                y - v_range
            ),
            'top-right': (
                x + h_range,
                y - v_range
            ),
            'bottom-left': (
                x - h_range,
                y + v_range
            ),
            'bottom-right': (
                x - h_range,
                y - v_range
            )
        }

    def _generate_coordinates(self):
        for x in xrange(self._h_led_count):
            for y in xrange(self._v_led_count):
                name = chr(ord('A') + x) + str(y + 1)
                self._inject_global_variables(name, (x, y))

                name = chr(ord('a') + x) + str(y + 1)
                self._inject_global_variables(name, (x, y))

    def _generate_global_helpers(self):
        self._inject_global_variables('LIGHT_WIDTH', 0)
        self._inject_global_variables('LIGHT_HEIGHT', 0)

        self._inject_global_variables('WIDTH', self._h_led_count)
        self._inject_global_variables('HEIGHT', self._v_led_count)

        self._inject_global_variables(
            'SIZE', (self._h_led_count, self._v_led_count)
        )

        self._inject_global_variables('TOPLEFT', (0, 0))
        self._inject_global_variables('TOPRIGHT', (self._h_led_count, 0))
        self._inject_global_variables('BOTTOMLEFT', (0, self._v_led_count))
        self._inject_global_variables('BOTTOMRIGHT', __builtins__['SIZE'])

        self.reset_exports()

    def _row_iter(self, loop=False):
        def row(row_no):
            for i in xrange(self._h_led_count):
                yield tuple((i, row_no))

        def all_rows():
            for row_no in xrange(self._v_led_count):
                for i in row(row_no):
                    yield i

        if loop:
            return itertools.cycle(all_rows())

        return all_rows()

    def reset_exports(self):
        self._inject_global_variables('board', self._row_iter())
        self._inject_global_variables('board_loop', self._row_iter(loop=True))
