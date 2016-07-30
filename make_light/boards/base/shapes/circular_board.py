# circular_board.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Implements methods for circular boards

from make_light.boards.base.simulation_board import SimulationBoard
from make_light.boards.base.coords.polar import Polar


class CircularBoard(SimulationBoard, Polar):
    LED_RINGS = [0]
    RING_RADII = [0]
    RING_THICKNESSES = [0]
    RING_OFFSETS = [0]

    def __init__(self):
        self._DIMENSIONS = self.IMAGE_DIMENSIONS

        SimulationBoard.__init__(self)
        Polar.__init__(self, self.LED_RINGS, self.RING_RADII,
                       self.RING_THICKNESSES, self.RING_OFFSETS)

    def on(self, *args, **kwargs):
        """
        This function has several use cases:
        light.on(position)
        light.on(position...)
        light.on(position..., intensity)
        light.on(position, colour=...)
        light.on(position, intensity, colour=...)
        light.on(position..., colour=...)
        light.on(position..., intensity, colour=...)
        light.on(all)
        light.on(all, intensity)
        light.on(all, colour=...)
        light.on(all, intensity, colour=...)

        when spec is not passed, it defaults to True
        When a list is passed, it is iterated over
        when 'all' is passed, we apply to all LEDs
        """
        leds, dummy_intensity = self._parse_coord_args(*args)
        fill = self._parse_colour_kwargs(**kwargs)

        for loc in leds:
            bounding_box = self.get_bounding_box(loc)
            bounding_sector = self.get_bounding_sector(loc)
            # FIXME: Draw only the arc, not the whole slice
            self._board_lights_draw.pieslice(
                ((0, 0), self.IMAGE_DIMENSIONS),
                bounding_sector['inner-left'][1],
                bounding_sector['inner-right'][1], fill=fill
            )

        self._update()

    def off(self, *args):
        if self.MONOCHROME:
            # Last argument is interpreted as intensity
            self.on(*args + (0.0,))
        else:
            self.on(*args, colour=__builtins__['black'])

    def arc(self, ring_no, start, end, **kwargs):
        '''
        @param radius  ring number
        @param start   angle or LED
        @param end     angle or LED
        '''

        if type(start) == tuple:
            start_bounding_sector = self.get_bounding_sector(start)
            start = start_bounding_sector['inner-left'][1]

        if type(end) == tuple:
            end_bounding_sector = self.get_bounding_sector(end)
            end = end_bounding_sector['inner-right'][1]

        fill = self._parse_colour_kwargs(**kwargs)
        self._board_lights_draw.pieslice(
            ((0, 0), self.IMAGE_DIMENSIONS), start, end, fill=fill
        )

        self._update()

    def circle(self, radius, **kwargs):
        CircularBoard.arc(self, radius, 0, 360, **kwargs)

    def all(self, *args, **kwargs):
        on = args[0] if args else True

        kwargs.update({'on': on})
        fill = self._parse_colour_kwargs(**kwargs)

        self._board_lights_draw.rectangle(((0, 0), self._DIMENSIONS), fill=fill)

        self._update()
