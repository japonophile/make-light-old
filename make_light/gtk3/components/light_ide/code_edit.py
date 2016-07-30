# code_edit.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Controls the widget where the user enters python code.
# A ssh trust relationship is setup automatically.
# Provides for transferring and executing the code remotely on the Powerup Kit unit


import os
import re

from gi.repository import Gtk, GtkSource, GObject

from kano.gtk3.scrolled_window import ScrolledWindow
from kano.logging import logger

from kano.utils import chown_path

from make_light.boards.router import BOARD_ROUTER
from make_light.gtk3.components.light_ide.make_button import MakeButton
from make_light.gtk3.dimensions import HEADER_BUTTON_HEIGHT
from make_light.paths import CHALLENGES_DIR, TEMP_DIR


class CodeEdit(Gtk.Box):
    """
    This class controls the code edit widget
    """

    tmp_file = os.path.join(TEMP_DIR, "powerup-code.py")
    tmp_fileA = os.path.join(TEMP_DIR, "powerup-code-all.py")
    preamble_length = 0
    code_length = 0

    tpath = CHALLENGES_DIR

    __gsignals__ = {
        "finished-process": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        "started-process": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        "code-changed": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
        'make': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'kill': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ())
    }

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        # container styling
        self.set_vexpand(True)
        self.get_style_context().add_class("code_edit")

        scrolled_window = ScrolledWindow()
        scrolled_window.apply_styling_to_widget()
        scrolled_window.set_margin_top(20)
        scrolled_window.set_margin_bottom(20)
        scrolled_window.set_margin_left(10)  # line numbers are already indented
        scrolled_window.set_margin_right(20)
        self.pack_start(scrolled_window, True, True, 0)

        # regexp for use with automatic indentation
        self.indent_re = re.compile(':\s*$')

        self.code = self.setup_code_widget()
        scrolled_window.add(self.code)

        self.make_button = MakeButton()
        self.make_button.connect('make', self._on_make)
        self.make_button.connect('kill', self._on_kill)
        self.make_button.set_size_request(-1, HEADER_BUTTON_HEIGHT)
        self.pack_start(self.make_button, False, False, 0)

        self.check_widget = CheckCodeWidget()
        self.pack_start(self.check_widget, False, False, 0)

        BOARD_ROUTER.connect('finished-run', self.finished_run)
        BOARD_ROUTER.connect('powerup-status', self.set_powerup_status)
        BOARD_ROUTER.connect('error', self.set_error)

    def _on_make(self, button=None):
        self.clear_error()

        # simply re-emiting the signals here
        self.emit('make')

    def _on_kill(self, button=None):
        # simply re-emiting the signals here
        self.emit('kill')

    def give_focus(self, window):
        window.set_focus(self.code)

    def set_powerup_status(self, widget, detected, setup_complete, powerup_available):
        """
        GUI actions related to powerup.

        Only inhibit make button when we have detected the powerup kit and are
        waiting for the initiial ssh to complete.

        Otherwise we will be using the simulator.
        """
        if detected and not powerup_available:
            if not setup_complete:
                message = 'Warming up...'
            else:
                message = 'Not connected'

            self.make_button.set_sensitive(False)

        elif powerup_available:

            message = 'Connected'
            self.check_widget.success()
            self.make_button.set_sensitive(True)

        else:
            message = 'Not connected'

        self.check_widget.set_text('The Powerup LED Kit is {}'.format(message))

    def hide_check_widget(self):
        self.check_widget.hide()

    def signal_code_changed(self, buffer):
        self.emit("code-changed", self)

    def _get_indentation_chars(self, source_view):
        indentation_chars = '\t'

        if source_view.get_insert_spaces_instead_of_tabs():
            width = source_view.get_indent_width()

            if width == -1:
                width = source_view.get_tab_width()

            indentation_chars = ''.join([' ' for dummy in xrange(width)])

        return indentation_chars

    def inserted(self, widget, location, inserted_text, length, source_view):
        # Check whether we should indent
        if inserted_text != "\n":
            return

        # User just pressed enter. Does the previous line end in colon?
        start = location.copy()
        start.backward_line()
        end = location
        prev_line_text = widget.get_text(start, end, False)

        if not self.indent_re.search(prev_line_text):
            return

        # Insert indentation:
        indentation_chars = self._get_indentation_chars(source_view)
        widget.insert(location, indentation_chars)

        # Revalidate location to avoid warnings from GTK
        cursor = widget.get_property('cursor-position')
        new_loc = widget.get_iter_at_offset(cursor)
        location.assign(new_loc)

    def setup_code_widget(self):
        buffer_python = GtkSource.Buffer()
        code = GtkSource.View.new_with_buffer(buffer_python)

        # Should add padding to text in the GtkSource.View
        code.set_left_margin(15)
        code.set_right_margin(15)

        code.set_show_line_numbers(True)
        code.set_border_window_size(Gtk.TextWindowType.TOP, Gtk.TextWindowType.BOTTOM)

        code.set_wrap_mode(True)
        code.set_insert_spaces_instead_of_tabs(False)
        code.set_tab_width(4)
        code.set_indent_width(4)
        # This enables replication of indentation on subsequent lines
        code.set_auto_indent(True)

        # Not sure this does much?
        code.set_highlight_current_line(False)

        lang_manager = GtkSource.LanguageManager()
        buffer_python.set_language(lang_manager.get_language('python'))
        buffer_python.connect("changed", self.signal_code_changed)
        buffer_python.connect_after("insert-text", self.inserted, code)

        code.get_style_context().add_class("code_edit")

        return code

    def get_code(self):
        code_buf = self.code.get_buffer()
        start_iter = code_buf.get_start_iter()
        end_iter = code_buf.get_end_iter()
        return code_buf.get_text(start_iter, end_iter, True)

    def get_last_code_line(self):
        code_buf = self.code.get_buffer()
        lines = code_buf.get_line_count()
        start_iter = code_buf.get_iter_at_line(lines - 1)
        end_iter = code_buf.get_end_iter()
        return code_buf.get_text(start_iter, end_iter, True)

    def set_code(self, text):
        """
        Put the text that makes up the code inside the view
        """
        self.code.get_buffer().set_text(text)

    def run_available(self):
        """
        return true if the lightboard is available
        """
        return True  # FIXME
        return self.runner.available

    def run_code(self):
        """
        Collects the code in the edit area.
        Embraces it inside preable and postamble code sections.
        Finally delegates the execution of the code to the remote PI1 or locally.

        This function is thread based to provide Gtk UI correct responsiveness
        """

        # Raise on progress event and remote send the code to the Powerup Kit
        self.emit("started-process")
        success = self._write_code_to_file()
        if not success:
            GObject.idle_add(
                self.finished_run, None, 'Error writing the code'
            )
            return

        # Disallow user from entering text in the code widget
        # Disabled until it works with the animation
        # self.code.set_sensitive(False)

        # Measure length of code and preamble (used when adjusting line number in error message)
        preamble = BOARD_ROUTER.board.preamble
        self.preamble_length = sum(1 for line in preamble.splitlines())

        with open(self.tmp_file, 'r') as f:
            code = f.read()
        self.code_length = sum(1 for line in code)

        postamble = BOARD_ROUTER.board.postamble

        # Extract the code to "Make" wrapped inside preamble and postamble sections
        try:
            with open(self.tmp_fileA, 'w') as f:
                f.write(preamble + code + postamble)
        except (IOError, OSError) as e:
            logger.error(
                'Error collecting code (preamble + postamble): {}'.format(e)
            )
            GObject.idle_add(self.finished_run, None,
                             'Error preprocessing the code')
            return
        else:
            chown_path(self.tmp_fileA)

        # If the lighboard is connected (Locally via serial or remotely via Ethernet to PI1)
        if self.run_available():
            BOARD_ROUTER.run_code(self.tmp_fileA)

    def connect_buffer_signal(self, *args):
        code_buf = self.code.get_buffer()
        code_buf.connect(*args)

    def kill_code(self):
        if BOARD_ROUTER.is_running():
            BOARD_ROUTER.kill_code()
        else:
            self.finished_run(None, '')

    def finished_run(self, widget, error):
        self.set_error(widget, error)
        # Disabled until it works with the animation
        # self.code.set_sensitive(True)
        # self.toggle_make(True)
        self.emit("finished-process")
        self.make_button.revert_to_make()

    def set_error(self, widget, stderr):
        if not stderr:
            return

        # scan the error message
        matches = re.search(r"File \"(?P<path>.+)\", line (?P<line>\d+).*\n\s+(?P<code>.*)\n(?:\s*\^\s*\n)?(?P<error>.+)$", stderr)
        if not matches:
            return
        results = matches.groupdict()

        if not matches:
            return
        results = matches.groupdict()

        # The line number is the line number from the final compiled code. To get the line number
        # in the user's code we need to subtract the length of the preamble
        line_number = int(results['line']) - self.preamble_length
        error_tb = ',\n\t\t'.join(results['error'].strip().split(','))

        if line_number <= self.code_length:
            error_message = 'Error on Line {}:\n\t{}'.format(
                line_number, error_tb
            )
        # syntax errors report the line number to be in the postamble, so we need to ignore
        # the line numbers and simply say there was an error
        else:
            error_message = 'Error:\n\t{}'.format(error_tb)

        self.check_widget.error()
        self.check_widget.set_text(error_message)

    def clear_error(self):
        self.check_widget.clear()

    def _write_code_to_file(self):
        code = self.get_code()

        try:
            with open(self.tmp_file, "w") as f:
                f.write(code)
        except (IOError, OSError) as exc_err:
            logger.error("Couldn't write the code to file [{}]".format(exc_err))
            return False

        chown_path(self.tmp_file)
        return True


class CheckCodeWidget(Gtk.Label):
    """
    This class is in charge of managing the status area of your
    code, below the code edit area.
    """

    def __init__(self):
        Gtk.Label.__init__(self)
        self.get_style_context().add_class("check_code")

    def error(self):
        self.get_style_context().add_class("error")
        self.get_style_context().remove_class("success")
        self.show_all()

    def clear(self):
        self.get_style_context().remove_class("error")
        self.get_style_context().remove_class("success")
        self.set_text("")

    def success(self):
        self.set_text("No errors - your syntax looks good!")
        self.get_style_context().remove_class("error")
        self.get_style_context().add_class("success")
        self.show_all()
