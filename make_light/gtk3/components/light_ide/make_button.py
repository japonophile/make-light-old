# make_button.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The make button. It emits a `kill` and a `make` event in addition
# to a clicked event.


from gi.repository import Gtk, GObject

from kano.gtk3.cursor import attach_cursor_events


class MakeButton(Gtk.Button):

    MAKE_TEXT = 'Make'.upper()  # TODO: i18n
    KILL_TEXT = 'Stop'.upper()  # TODO: i18n

    MAKE_MODE = True  # is False when it is a kill button

    DISABLE_TIME = 2000  # ms

    # For an explanation on why custom signals are registered like this
    # http://python-gtk-3-tutorial.readthedocs.org/en/latest/objects.html#signals
    #
    __gsignals__ = {
        # Define custom events that the main UI will listen for
        'make': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_BOOLEAN, ()),
        'kill': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_BOOLEAN, ())
    }

    def __init__(self):
        Gtk.Button.__init__(self, self.MAKE_TEXT)

        self.get_style_context().add_class('light-ide-make-button')
        attach_cursor_events(self)

        self.connect('clicked', self._on_click)

    def revert_to_make(self):
        """
        This is called when the animation finishes, and we
        need to revert the button back to the orange 'MAKE'
        """
        self._re_enable()
        self._revert_to_make()

    def _on_click(self, widget=None):
        # trigger kill or make events depending on state
        self.set_sensitive(False)
        GObject.timeout_add(self.DISABLE_TIME, self._re_enable)

        if self.MAKE_MODE:
            self.emit('make')
            self._revert_to_stop()
        else:
            self.emit('kill')
            self._revert_to_make()

    def _revert_to_make(self):
        self.MAKE_MODE = True
        self.set_label(self.MAKE_TEXT)
        self.get_style_context().add_class('light-ide-make-button')
        self.get_style_context().remove_class('light-ide-stop-button')

    def _revert_to_stop(self):
        self.MAKE_MODE = False
        self.set_label(self.KILL_TEXT)
        self.get_style_context().add_class('light-ide-stop-button')
        self.get_style_context().remove_class('light-ide-make-button')

    def _re_enable(self):
        # if the animation finished before the callback was executed
        # the button is already enabled
        if self.get_sensitive() is False:
            self.set_sensitive(True)

        return False  # stop callback from being called again
