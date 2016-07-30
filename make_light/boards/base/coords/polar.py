# polar.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Implements methods for polar coordinates

import itertools

from make_light.boards.base.coords.coords import Coords


class Ring(object):

    def __init__(self, led_count, radius, thickness, offset):
        self.led_count = led_count
        self._angular_spacing = 360 / self.led_count
        self.radius = radius
        self._thickness = thickness
        self._offset = offset

    def __len__(self):
        return self.led_count

    def get_addr_from_angle(self, angle):
        return int((self._angular_spacing - self._offset) / angle)

    def get_led_angle(self, led_idx):
        return led_idx * self._angular_spacing + self._offset

    def get_led_coords(self, led_idx):
        return (
            self.radius,
            self.get_led_angle(led_idx)
        )

    def get_bounding_sector(self, led_idx):
        theta = self.get_led_angle(led_idx)
        theta_range = self._angular_spacing / 2
        radius_range = self._thickness / 2

        return {
            'outer-left': (
                self.radius + radius_range,
                theta - theta_range
            ),
            'outer-right': (
                self.radius + radius_range,
                theta + theta_range
            ),
            'inner-left': (
                self.radius - radius_range,
                theta - theta_range
            ),
            'inner-right': (
                self.radius - radius_range,
                theta + theta_range
            ),
        }


class Polar(Coords):

    # TODO: Make some optional
    def __init__(self, led_rings, ring_radii,
                 ring_thicknesses, ring_offsets):

        assert len(led_rings) == \
            len(ring_offsets) == \
            len(ring_radii) == \
            len(ring_thicknesses)

        self._rings = [
            Ring(led_count, radius, thickness, offset)
            for led_count, radius, thickness, offset
            in zip(led_rings, ring_radii, ring_thicknesses, ring_offsets)
        ]

        super(Polar, self).__init__()

    def get_addr_from_coords(self, coords):
        r, theta = coords

        return r, self._rings[r].get_addr_from_angle(theta)

    def get_coords(self, addr):
        ring, led_idx = addr
        return self._rings[ring].get_led_coords(led_idx)

    def get_bounding_sector(self, addr):
        ring, led_idx = addr
        return self._rings[ring].get_bounding_sector(led_idx)

    def get_bounding_box(self, addr):
        bounding_sector = self.get_bounding_sector(addr)
        cartesians = [
            Coords.polar_to_cartesian(*polar) for polar \
            in bounding_sector.values()
        ]

        x_vals, y_vals = zip(*cartesians)

        return (
            (min(x_vals), min(y_vals)),
            (max(x_vals), max(y_vals))
        )


    def _generate_coordinates(self):
        for ring_no, ring in enumerate(self._rings):
            for led_no in xrange(len(ring)):
                name = chr(ord('A') + ring_no) + str(led_no + 1)
                self._inject_global_variables(name, (ring_no, led_no))

                name = chr(ord('a') + ring_no) + str(led_no + 1)
                self._inject_global_variables(name, (ring_no, led_no))

    def _generate_global_helpers(self):
        self.reset_exports()

    def _ring_iter(self, loop=False):
        def ring(ring_no):
            led_count = len(self._rings[ring_no])
            for i in xrange(led_count):
                yield tuple((ring_no, i))

        def all_rings():
            for ring_no, dummy in enumerate(self._rings):
                for i in ring(ring_no):
                    yield i

        if loop:
            return itertools.cycle(all_rings())

        return all_rings()

    def reset_exports(self):
        self._inject_global_variables('board', self._ring_iter())
        self._inject_global_variables('baord_loop', self._ring_iter(loop=True))
