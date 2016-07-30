# __init__.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Init file for module that routes commands from the app to the boards

import os
from gi.repository import GObject

from kano.logging import logger

from make_light.boards.router.runners.lightboard_runner import LightBoardRunner
from make_light.boards.router.runners.lightboard_runner_local import \
    LightBoardRunnerLocal
from make_light.boards.router.runners.lightboard_runner_ethernet import \
    LightBoardRunnerEthernet
from make_light.boards.router.runners.simulation_runner import SimulationRunner
from make_light.boards.available_boards import AVAILABLE_BOARDS


class BoardNotSupportedError(NotImplementedError):
    """ Exception class used when we try to use a board that is not yet
    supported.
    Information about the issue will be contained in the instance variable
    `message`.

    Error messages included in this exception class are automatically logged
    using the Kano logger (you are welcome).
    """
    def __init__(self, *args, **kwargs):
        super(BoardNotSupportedError, self).__init__(*args, **kwargs)
        # Once the Exception is thrown, log it
        try:
            from kano.logging import logger as log
            log.error(self.message)
        except ImportError:
            pass


class BoardRouter(GObject.GObject):

    __gsignals__ = {
        'gif-encoded': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'plug-loaded': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'plug-error': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                       (GObject.TYPE_PYOBJECT,)),
        'finished-run': (GObject.SIGNAL_RUN_FIRST, None,
                         (GObject.TYPE_STRING,)),
        'powerup-status': (GObject.SIGNAL_RUN_FIRST, None,
                           (GObject.TYPE_BOOLEAN,
                            GObject.TYPE_BOOLEAN,
                            GObject.TYPE_BOOLEAN,)),
        'error': (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_STRING,)),
        'changed-board': (GObject.SIGNAL_RUN_FIRST, None,
                          (GObject.TYPE_STRING,)),
    }

    def __init__(self, board_name, simulation_enabled=True,
                 run_locally=True, run_remotely=False):
        GObject.GObject.__init__(self)

        self.board = None
        self.hw_board = None
        self._anim_socket = None

        self._connected_signals = {}

        self.simulation_enabled = simulation_enabled
        self.run_locally = run_locally
        self.run_remotely = run_remotely

        self._simulation_runner = \
            self._local_runner = \
            self._remote_runner = LightBoardRunner(self.board)

        self.change_board(board_name)

        self._simulation_launched = False

    def change_board(self, board_name):
        """ Change the board instance to a new instance of a board with the
        corresponding name

        if the board doesn't exist this function will raise
        BoardNotSupportedError

        Once the new board is selected, the `changed-board` GObject signal will
        be emitted
        :param board_name: Nane of the board to change to
        :type board_name: basestring
        :raises: BoardNotSupportedError iff no board corresponds to the given
                 name
        """
        try:
            if self.hw_board:
                self.hw_board._clean_up()

            self.board = self._load_board_by_name(board_name, hw=False)
            self.hw_board = self._load_board_by_name(board_name, hw=True)

            self.destroy_hw_runners()
            self.initialise_hw_runners()
            self.emit('changed-board', self.board.NAME)
        except ImportError:
            raise BoardNotSupportedError(
                'Tried to change to board named "{}"'.format(board_name)
            )

    def is_current_board(self, board_name):
        return board_name == self.board.NAME

    def initialise_hw_runners(self):
        if self.run_locally:
            if self.hw_board.detect_board():
                self._local_runner = LightBoardRunnerLocal(self.hw_board)
            else:
                self._local_runner = None
        else:
            self._local_runner = None

        if self.run_remotely:
            # Bring up the networking between the 2 RaspberryPIs
            rc = os.system('sudo /usr/bin/powerup-network -u')
            if rc == 0:
                self._remote_runner = LightBoardRunnerEthernet(self.hw_board)
            else:
                self._remote_runner = None
        else:
            self._remote_runner = None

    @staticmethod
    def _destroy_runner(runner):
        if hasattr(runner, 'kill_animation_process'):
            try:
                runner.kill_animation_process()
            except Exception as exc:
                logger.warn("Couldn't kill animation process [{}]".format(exc))
        else:
            if hasattr(runner, 'kill_code'):
                try:
                    runner.kill_code()
                except NotImplementedError:
                    pass
                except Exception as exc:
                    logger.warn("Couldn't kill code [{}]".format(exc))

    def destroy_hw_runners(self):
        self._destroy_runner(self._simulation_runner)
        self._destroy_runner(self._local_runner)
        self._destroy_runner(self._remote_runner)

    def set_animation_socket(self, anim_socket):
        if not self.simulation_enabled:
            return

        self._anim_socket = anim_socket

        if self._simulation_launched:
            if self._simulation_runner.is_running():
                try:
                    self._simulation_runner.destroy()
                except OSError:
                    # We get this if this process is already terminated
                    pass

        self._create_simulation_runner()

    @classmethod
    def _load_board_by_name(cls, board_name, hw=False):
        board = AVAILABLE_BOARDS[board_name]

        if hw:
            return board['physical_board']()
        else:
            return board['simulation_board']()

    def _create_simulation_runner(self):
        if not self._anim_socket:
            raise ValueError('A valid animation socket is required')

        self._simulation_runner = runner = SimulationRunner(
            self.board, self._anim_socket
        )
        runner.connect('finished-run', self._on_finished_run)
        runner.connect('gif-encoded', self._on_gif_encoded)
        runner.connect('plug-loaded', self._on_plug_loaded)
        runner.connect('plug-error', self._on_plug_error)

        self._simulation_launched = True

    def _do_run_simulation(self):
        if not self.simulation_enabled:
            return

        self._simulation_runner.run_code()

    def start_animation_process(self):
        self._simulation_runner.start_animation_process()

    def _do_run_locally(self, filename):
        if not self.run_locally or self._local_runner is None:
            return

        runner = self._local_runner
        # runner.connect('finished-run', self._on_finished_run_suppressed)
        runner.connect('powerup-status', self._on_powerup_status)
        runner.connect('error', self._on_error)
        runner.run_code(filename)

    def _do_run_remotely(self, filename):
        if not self.run_remotely or self._remote_runner is None:
            return

        runner = self._remote_runner
        # runner.connect('finished-run', self._on_finished_run_suppressed)
        runner.connect('powerup-status', self._on_powerup_status)
        runner.connect('error', self._on_error)
        runner.run_code(filename)

    def _on_finished_run(self, obj, *args, **kwargs):
        self.emit('finished-run', *args, **kwargs)

    def _on_finished_run_suppressed(self, widget=None, err_str=''):
        # Log the error instead of propagating it to the app
        if err_str:
            logger.warn(
                'Got error from HW runner [{}]'
                .format(err_str.encode('string_escape'))
            )
        self.emit('finished-run', '')

    def _on_gif_encoded(self, obj, *args, **kwargs):
        self.emit('gif-encoded', *args, **kwargs)

    def _on_plug_loaded(self, obj, *args, **kwargs):
        self.emit('plug-loaded', *args, **kwargs)

    def _on_plug_error(self, obj, *args, **kwargs):
        self.emit('plug-error', *args, **kwargs)

    def _on_powerup_status(self, obj, *args, **kwargs):
        self.emit('powerup-status', *args, **kwargs)

    def _on_error(self, obj, *args, **kwargs):
        self.emit('error', *args, **kwargs)

    def run_code(self, filename):
        self._do_run_simulation()
        self._do_run_locally(filename)
        self._do_run_remotely(filename)

    def is_running(self):
        return (
            (self._simulation_runner and self._simulation_runner.is_running())
            or (self._local_runner and self._local_runner.is_running())
            or (self._remote_runner and self._remote_runner.is_running())
        )

    def save_animation(self):
        self._simulation_runner.save_animation()

    def kill_code(self):
        try:
            self._simulation_runner.kill_code()
        except NotImplementedError:
            pass

        try:
            if self._local_runner:
                self._local_runner.kill_code()
        except NotImplementedError:
            pass

        try:
            if self._remote_runner:
                self._remote_runner.kill_code()
        except NotImplementedError:
            pass

    def connect(self, signal, handler, *args, **kwargs):
        '''
        The BOARD_ROUTER object is reused around the application in many
        different contexts. This allows several attempts to set event handlers
        when it is in a different context. Prevent this by removing the previous
        one.
        '''

        old_handler = self._connected_signals.get(signal, False)

        if old_handler:
            self.disconnect(old_handler)

        handler_id = GObject.GObject.connect(
            self, signal, handler, *args, **kwargs
        )
        self._connected_signals[signal] = handler_id


BOARD_ROUTER = BoardRouter('Lightboard', simulation_enabled=True,
                           run_locally=True, run_remotely=False)
