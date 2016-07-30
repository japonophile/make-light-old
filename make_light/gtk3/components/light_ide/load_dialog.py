# load_dialog.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Used to select previously saved files or shares to load in Playground

from gi.repository import Gtk

from make_light.paths import SAVE_DIR, CODE_FILE_EXTENSION

class LoadDialog(Gtk.FileChooserDialog):

    def __init__(self, parent=None):
        Gtk.FileChooserDialog.__init__(
            self,
            'Please choose a file',
            parent,
            Gtk.FileChooserAction.OPEN, (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK
            )
        )
        self.set_current_folder(SAVE_DIR)  # meh

        file_filter = Gtk.FileFilter()
        file_filter.set_name('LightCode')
        file_filter.add_pattern('*.{}'.format(CODE_FILE_EXTENSION))
        self.add_filter(file_filter)
