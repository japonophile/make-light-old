# physical_board.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Defines interfaces for the led board

import os
import time
import atexit

from kano_peripherals.speaker_leds.driver.high_level import \
    get_speakerleds_interface
from kano.logging import logger

from make_light.boards.base.physical_board import PhysicalBoard
from make_light.boards.base.coords.polar import Polar


def ensure_api(func):
    '''
    Decorator to ensure that everything in the API is functioning correctly
    before attempting to use it.
    '''

    def handle_errors(*args, **kwargs):
        self = args[0]

        if not self.api:
            logger.error('No API to connect to. '
                         'Ensure that `kano-boards-daemon` is running.')
            return None

        return func(*args, **kwargs)

    return handle_errors


class LEDSpeakerPhysical(PhysicalBoard, Polar):
    """
    This is the LED Speaker API for Make Light.

    Methods without a leading underscore are indended as user methods.

    Methods with one leading underscore are public inside Make Light source.
    Methods with two leading underscores are private.
    """

    def __init__(self):
        PhysicalBoard.__init__(self)
        Polar.__init__(self, led_rings=[10], ring_radii=[0],
                       ring_thicknesses=[0], ring_offsets=[0])

        # NOTE: can be '' if the lock could not be acquired which
        #       will cause dbus api calls to return FALSE
        self.token = os.environ['API_TOKEN'] if 'API_TOKEN' in os.environ else ''

        self.api = get_speakerleds_interface()  # TODO: can be None

        if not self.api:
            return

        self.__lock()
        atexit.register(self._clean_up)

        self.num_leds = self.api.get_num_leds()

    @ensure_api
    def detect_board(self):
        return self.api.detect()

    def clear(self):
        self.__set_leds_off()

    def on(self, *args, **kwargs):
        leds, dummy_intensity = self._parse_coord_args(*args)
        kwargs.update({'normalise': True})
        col = self._parse_colour_kwargs(**kwargs)

        for led in leds:
            self.__set_led(led[1], col)

    def off(self, *args):
        leds, dummy_intensity = self._parse_coord_args(*args)
        col = self.normalise_colour(__builtins__['black'])
        for led in args:
            self.__set_led(led[1], col)

    def all(self, **kwargs):
        kwargs.update({'normalise': True})
        col = self._parse_colour_kwargs(**kwargs)
        arg = [col for dummy in xrange(self.num_leds)]
        self.__set_all_leds(arg)

    def circle(self, **kwargs):
        self.all(**kwargs)

    def arc(self, start, end, **kwargs):
        kwargs.update({'normalise': True})
        col = self._parse_colour_kwargs(**kwargs)

        if type(start) == tuple:
            dummy, start_idx = start
        else:
            start_idx = self.get_addr_from_coords((0, start))[1]

        if type(start) == tuple:
            dummy, end_idx = end
        else:
            end_idx = self.get_addr_from_coords((0, end))[1]

        if start_idx > end_idx:
            end_idx += self.num_leds

        for i in xrange(start_idx, end_idx + 1):
            self.__set_led(i % self.num_leds, col)

    def spin(self, delay, **kwargs):
        col = self._parse_colour_kwargs(**kwargs)

        for led in __builtins__['board']:
            self.on(led, colour=col)
            time.sleep(delay)
            self.clear()

    def _clean_up(self):
        """
        Release all resources used by this object.

        Unlocking the LED Speaker API here and removing the lock token.
        The method gets executed whenever the Hardware is changed
        or the app quits.
        """
        if self.token:
            self.api.unlock()
            os.environ.pop('API_TOKEN', None)

    def _get_api_token(self):
        return self.token

    @ensure_api
    def __lock(self):
        """
        Lock LED Speaker API from other apps.

        Gets exclusive access on the LED Speaker so no other apps can use it.
        The lock token is acquired by Make Light and the AnimationPlug uses the
        one saved in os.environ (does not lock again).
        """
        if self.token:
            return False

        max_lock_priority = self.api.get_max_lock_priority()
        self.token = self.api.lock(max_lock_priority)
        if not self.token:
            logger.warn('LEDSpeakerPhysical could not acquire lock with'
                        ' maximum priority {}!'.format(max_lock_priority))

            for priority in xrange(max_lock_priority, 0, -1):
                self.token = self.api.lock(priority)

                if self.token:
                    logger.warn('LEDSpeakerPhysical eventually acquired'
                                ' lock with priority {}!'.format(priority))
                    break

            if not self.token:
                logger.warn('LEDSpeakerPhysical could not acquire lock!')

        os.environ['API_TOKEN'] = self.token

    @ensure_api
    def __set_leds_off(self):
        if self.token:
            return self.api.set_leds_off_with_token(self.token)
        else:
            return self.api.set_leds_off()

    @ensure_api
    def __set_all_leds(self, values):
        if self.token:
            return self.api.set_all_leds_with_token(values, self.token)
        else:
            return self.api.set_all_leds(values)

    @ensure_api
    def __set_led(self, num, rgb):
        '''
        FIXME: This translation layer is required to align A1 with north on the board.
               This should be moved into the API itself.
        '''
        num = (num - 3) % self.num_leds

        if self.token:
            return self.api.set_led_with_token(num, rgb, self.token)
        else:
            return self.api.set_led(num, rgb)


class Board(LEDSpeakerPhysical):
    pass
