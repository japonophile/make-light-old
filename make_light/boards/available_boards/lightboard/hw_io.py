# hw_io.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# HW API for accessing the Lightboard

import os
import serial
import collections
import numbers
from contextlib import contextmanager
from array import array
from time import sleep

from PIL import Image, ImageDraw, ImageFont, ImageColor

from kano.logging import logger

from make_light.paths import FONTS_DIR


class LightBoardError(RuntimeError):
    """ Exception class used for the HW API for the Kano LightBoard.
    Information about the issue will be contained in the instance variable
    `message`.

    Error messages included in this exception class are automatically logged
    using the Kano logger (you are welcome).
    """
    def __init__(self, *args, **kwargs):
        super(LightBoardError, self).__init__(*args, **kwargs)
        # Once the Exception is thrown, log it
        try:
            from kano.logging import logger as log
            log.error(self.message)
        except ImportError:
            pass


@contextmanager
def _safe_access(lock):
    """ This can be used in with a context manager to handle getting and putting
    a lock while trying to access a shared resource
    """
    if lock is not None:
        with lock:
            yield
    else:
        yield


@contextmanager
def open_serial(*args, **kwargs):
    """ Please note that this is to be used as a 'with' statement conext
    managers.
    Creates a new connection using Serial using the arguments that are
    passed to it and provides the handle to that connection.
    :raises ValueError: when the parameters passed to Serial are not out of
                        range
    :raises RuntimeError: When the device can't be configured
    """
    lock = kwargs.pop('lock', None)
    try:
        with _safe_access(lock):
            interface = serial.Serial(*args, **kwargs)
            yield interface
            interface.close()
    except ValueError as exc_err:
        raise LightBoardError(
            "Couldn't open the device, parameters out of range [{}]"
            .format(exc_err)
        )
    except serial.SerialException as exc_err:
        raise LightBoardError(
            "Device couldn't be configured [{}]"
            .format(exc_err)
        )


class LightBoardCommsDriver(object):
    """ This class can be used as a driver for the LightBoard. To avoid
    concurrency issues, it can be used with a lock, to allow exclusive access
    to the hardware. Note this class doesn't hold a lock throughout its
    lifetime, but only while it is updating the board.
    """
    _instance = None
    DEV = '/dev/ttyS0' if os.path.exists('/dev/ttyS0') else '/dev/ttyAMA0'
    # A baud rate of 250000 is ideal, but pyserial needs to be patched to
    # accept this value
    BAUD = 38400
    LIGHT_WIDTH = 9
    LIGHT_HEIGHT = 14
    NUM_LEDS = LIGHT_WIDTH * LIGHT_HEIGHT
    LIGHTBOARD_SIGNATURE = 'KANO light board 1.0\r\n'

    @staticmethod
    def get_inst(lock=None):
        """ Get the (singleton) instance of the this class
        """
        if not LightBoardCommsDriver._instance:
            LightBoardCommsDriver._instance = LightBoardCommsDriver(lock)

        return LightBoardCommsDriver._instance

    def __init__(self, lock=None):
        """ Please do not use this constructor on its own, but rather call the
        LightBoardCommsDriver.get_inst() method
        :param lock: Shared lock to be used when trying to access this resource
        :type lock: threading.Lock
        """
        self._dev = self.DEV
        self._lock = lock

    def _write_raw(self, packet):
        """ Opens a serial connection to the device and writes whatever is
        provided as an input
        :param packet: Raw data to be written to serial device
        :type packet: bytearray or string
        :returns: True iff writin to device was successful, False otherwise
        :rtype: bool
        """
        try:
            serial_handle = open_serial(
                self._dev,
                self.BAUD,
                timeout=0.1,
                writeTimeout=0.1,
                lock=self._lock
            )
            with serial_handle as interface:
                interface.write(packet)
        except LightBoardError:
            return False
        except serial.SerialTimeoutException:
            logger.error(
                'Received timeout while trying to write to serial device'
            )
            return False
        return True

    def update_board(self, led_values):
        """ Pass a flattened list of pixel colour values to display on the board
        :param led_values: List containing the colour values to be passed to
                           the board. The numbers contained must be in the range
                           [0, 255]
        :types led_values: list of ints
        :returns: True iff communication to the board was successful
        :rtype: bool
        """
        # We need to prepend the \x55 char before sending board data
        sanitised_array = array('B', (int('0x55', 16),))

        # Pad the input with zeroes if the length is not right
        if len(led_values) < self.NUM_LEDS:
            padding_needed = self.NUM_LEDS - len(led_values)
            list_slice = led_values
        else:
            padding_needed = 0
            list_slice = led_values[0: self.NUM_LEDS]

        sanitised_array.fromlist(list_slice + padding_needed * [0])

        packet = bytearray(sanitised_array)

        ret = self._write_raw(packet)

        return ret

    def clear_board(self):
        """ Update with zeroes. Can be very useful when we want to clear the
        display.
        """
        self.update_board([0] * self.NUM_LEDS)

    def _detect_board_trigger(self):
        """ The light board should respond to a byte \0x54 with
        LIGHTBOARD_SIGNATURE
        :returns: Whether the board is present
        :rtype: Boolean
        """
        try:
            serial_handle = open_serial(
                self._dev,
                LightBoardCommsDriver.BAUD,
                timeout=0.1,
                writeTimeout=0.1,
                lock=self._lock
            )
            with serial_handle as interface:
                interface.write('\x54')
                res = interface.read(len(self.LIGHTBOARD_SIGNATURE))
        except LightBoardError:
            return False
        except serial.SerialTimeoutException:
            logger.error(
                'Received timeout while trying to write to serial device'
            )
            return False
        else:
            return res == self.LIGHTBOARD_SIGNATURE

    def detect_board(self):
        """ Attempts to connect to the board and to check whether it responds
        with a specific message. In case of a failure, it attempts to clear the
        screen and try again (to correct a potentially incorrect state)
        """
        res = self._detect_board_trigger()
        if not res:
            # We might be stuck in the middle of a frame, so if we get an
            # error try realigning
            self.clear_board()
            res = self._detect_board_trigger()
        logger.debug("looking for lightboard: found={}".format(res))
        return res


class LightBoardHW(object):
    """ Class that acts as a higher level lightboard HW driver. It maintains an
    internal representation of the lightboard and exposes a few higher level
    functions to draw basic shapes and animations
    """
    ASPECT_RATIO = 1.76
    FONT = ImageFont.load(os.path.join(FONTS_DIR, 'atari-small.pil'))
    LIGHT_WIDTH = 9
    LIGHT_HEIGHT = 14
    _DIMENSIONS = (LIGHT_WIDTH, LIGHT_HEIGHT)
    NUM_LEDS = LIGHT_WIDTH * LIGHT_HEIGHT

    BLACK = ImageColor.getcolor("black", "L")
    WHITE = ImageColor.getcolor("white", "L")
    COLORS = [
        ImageColor.getcolor("rgb({},{},{})".format(i, i, i), "L")
        for i in range(16, 256 + 16, 32)
    ]

    def __init__(self):
        self._lights_mode = 'L'
        self._board_lights_image = Image.new(
            self._lights_mode, self._DIMENSIONS
        )
        self._board_lights_draw = ImageDraw.Draw(self._board_lights_image)
        self._driver = LightBoardCommsDriver.get_inst()
        # By default this class is synchronous
        self._async = False

    def detect_board(self):
        """ Attempts to access the hardware and verify it is there.
        :returns: True iff board is accessible
        :rtype: bool
        """
        return self._driver.detect_board()

    def set_async(self):
        """ Set the driver to be asynchronous, i.e.  not update the hardware
        every time a command is issued. A flush or update_board would need to
        be called.
        """
        self._async = True

    def set_sync(self):
        """ Set the driver to be synchronous, i.e. update the hardware every
        time a command is issued
        """
        self._async = False

    def flush(self):
        """ Updates the board and then resets the canvas
        """
        self.update_board()
        switched_to_async = False
        if not self._async:
            self.set_async()
            switched_to_async = True
        self.set_to_all(False)
        if switched_to_async:
            self.set_sync()

    def update_board(self):
        """ Send the internally represented state to then HW. Similar to flush()
        but it doesn't clear the internal board after successful operation
        """
        dat = [x >> 5 for x in self._board_lights_image.getdata()]
        self._driver.update_board(dat)

    def _get_color(self, spec):
        """ Translate the spec to the appropriate colour
        """
        if spec is True:
            return self.WHITE
        elif spec is False:
            return self.BLACK
        elif isinstance(spec, int):
            return self.COLORS[max(0, min(7, spec))]
        elif isinstance(spec, float):
            return self.COLORS[max(0, min(7, int(spec * 8)))]

    def set_elements(self, positions, intensity):
        """ Turn specific pixels on
        :param positions: Sequence of 2-tuples
        :type positions: Sequence of 2-tuples i.e. [(int, int), ]
        :param intensity: Intensity to be used in the points given
        :type intensity: int from 0 to 255 ? or boolean
        """
        if not isinstance(positions, collections.Sequence):
            raise TypeError("positions argument must be a sequence type")

        if not isinstance(intensity, numbers.Number):
            raise TypeError(
                "intensity argument must be numeric type or boolean"
            )

        fill = self._get_color(intensity)
        self._board_lights_draw.point(positions, fill=fill)
        if not self._async:
            self.update_board()

    def unset_elements(self, positions):
        """ Turn specific pixels completely off
        :param positions: Sequence of 2-tuples
        :type positions: Sequence of 2-tuples i.e. [(int, int), ]
        """
        self.set_elements(positions, False)

    def set_to_all(self, spec):
        """ Apply a specific spec/colour to all the pixels of the board
        """
        fill = self._get_color(spec)

        self._board_lights_draw.rectangle(((0, 0), self._DIMENSIONS), fill=fill)

        if not self._async:
            self.update_board()

    def rectangle(self, A, B, spec=True):
        """ Draw a rectangle on the board
        """
        fill = self._get_color(spec)

        self._board_lights_draw.rectangle((A, B), fill=fill)

        if not self._async:
            self.update_board()

    def line(self, A, B, spec=True):
        """ Draw a line on the board
        """
        fill = self._get_color(spec)

        self._board_lights_draw.line((A, B), fill=fill)

        if not self._async:
            self.update_board()

    def circle(self, size, where, spec=True):
        """ Draw a circle on the board
        """
        fill = self._get_color(spec)
        x, y = where
        xsize = size * (1 / self.ASPECT_RATIO)
        self._board_lights_draw.ellipse(
            (
                (x - int(xsize / 2), y - int(size / 2)),
                (x + int(xsize / 2), y + int(size / 2))
            ),
            fill
        )
        if not self._async:
            self.update_board()

    def ellipse(self, A, B, spec=True):
        """ Draw an ellipse on the board
        """
        fill = self._get_color(spec)

        self._board_lights_draw.ellipse((A, B), fill=fill)
        if not self._async:
            self.update_board()

    def arc(self, middle, start, end, spec=True):
        """ Draw an arc on the board
        """
        fill = self._get_color(spec)

        self._board_lights_draw.arc(middle, start, end, fill=fill)
        if not self._async:
            self.update_board()

    def triangle(self, a, b, c, spec=True):
        """ Draw a triangle on the board
        """
        fill = self._get_color(spec)

        self._board_lights_draw.polygon([a, b, c], fill=fill)
        if not self._async:
            self.update_board()

    def polygon(self, points, spec=True):
        """ Draw a polygon on the board
        """
        fill = self._get_color(spec)

        self._board_lights_draw.polygon(points, fill=fill)
        if not self._async:
            self.update_board()

    def scroll(self, text, delay=0.1, portrait=False, top=3):
        """ Scroll a text string on the board
        """
        if portrait:
            raise NotImplementedError
        text = text + '    '
        (text_width, text_height) = self.FONT.getsize(text)
        for i in xrange(text_width):
            self._board_lights_draw.rectangle(
                ((self.LIGHT_WIDTH - i, 0), self._DIMENSIONS),
                fill=self.BLACK
            )
            self._board_lights_draw.text(
                (self.LIGHT_WIDTH - i, top), text, font=self.FONT,
                fill=self.WHITE
            )
            sleep(delay)
            if not self._async:
                self.update_board()

    def text(self, where, text):
        """ Display text on the board
        """
        self._board_lights_draw.text(
            where, text, font=self.FONT, fill=self.WHITE
        )
        if not self._async:
            self.update_board()
