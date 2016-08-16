# save_dialog.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


import os

from gi.repository import Gtk

from kano.gtk3.cursor import attach_cursor_events
from kano.gtk3.buttons import KanoButton

from kano.gtk3.multiline_entry import MultilineEntry
from make_light.paths import ICONS_DIR, IMAGES_DIR, GIF_DIR, GIF_FILE_NAME


class TemplateDialog(Gtk.Dialog):
    '''
    '''

    WIDTH = 800
    HEIGHT = -1  # mainly defined by the GIF animation height

    def __init__(self, widget, parent, title):
        Gtk.Dialog.__init__(self, parent=parent)
        self.parent = parent

        self.set_decorated(False)  # custom top bar
        self.set_resizable(False)  # do not resize the dialog
        self.set_skip_taskbar_hint(True)  # hide dialog from taskbar
        self.set_size_request(self.WIDTH, self.HEIGHT)
        self.get_style_context().add_class('dialog')
        self.parent.blur()

        # the dialog receives a signal when the GIF has been created
        widget.connect('gif-encoded', self._replace_gif_placeholder)
        widget.connect('plug-error', self._on_plug_error)
        self.replaced_placeholder = False

        # dialog layout structure
        window_grid = Gtk.Grid()
        window_grid.set_row_spacing(10)
        window_grid.set_column_spacing(20)
        window_grid.set_margin_left(20)
        window_grid.set_margin_right(20)
        window_grid.set_margin_bottom(20)
        self.get_content_area().pack_start(window_grid, True, True, 10)

        # the dialog close button
        close_button = Gtk.Button()
        close_button_image = Gtk.Image.new_from_file(
            os.path.join(ICONS_DIR, 'cross.png')
        )
        close_button.set_image(close_button_image)
        close_button.connect('clicked', self._close)
        close_button.get_style_context().add_class('dialog-close-button')
        attach_cursor_events(close_button)
        box = Gtk.Box()
        box.pack_end(close_button, False, False, 0)
        window_grid.attach(box, 0, 0, 2, 1)

        # the dialog header label
        header_label = Gtk.Label(_('{} ANIMATION').format(title))
        header_label.get_style_context().add_class('dialog-header-text')
        window_grid.attach(header_label, 0, 1, 2, 1)

        # the GIF animation on the left
        self.gif = Gtk.Image.new_from_file(
            os.path.join(IMAGES_DIR, 'loading-gif.gif')
        )
        window_grid.attach(self.gif, 0, 2, 1, 1)

        # the layout on the right
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        window_grid.attach(box, 1, 2, 1, 1)

        # 'Title' one line entry
        self.title_entry = Gtk.Entry()
        self.title_entry.set_max_length(200)
        self.title_entry.set_placeholder_text(_('Title'))
        self.title_entry.connect('changed', self._validate_input)
        box.pack_start(self.title_entry, False, False, 0)

        # 'Description' multiline entry
        self.description_entry = MultilineEntry()
        self.description_entry.set_max_length(500)
        self.description_entry.set_placeholder_text(_('Description'))
        box.pack_start(self.description_entry, True, True, 10)

        # SHARE / SAVE button
        self.button = KanoButton(title)
        self.button.connect('clicked', self._button_clicked)
        self.button.set_halign(Gtk.Align.CENTER)
        box.pack_start(self.button, False, False, 0)

        # set the button sensitive and show all
        self._validate_input()
        self.show_all()

    def _validate_input(self, *dummy_args, **dummy_kwargs):
        self.button.set_sensitive(
            self.title_entry.get_text().strip() != ''
            and
            self.replaced_placeholder
        )

    def _replace_gif_placeholder(self, widget=None):
        self.gif.set_from_file(os.path.join(GIF_DIR, GIF_FILE_NAME))
        self.queue_draw()  # redraw the entire widget
        self.replaced_placeholder = True
        self._validate_input()

    def _on_plug_error(self, widget=None, error=None):
        self._close()

    def _button_clicked(self, button=None):
        # TODO: when this finishes, a Warning is issued about a handler id
        self.response(Gtk.ResponseType.OK)
        self.data = {
            'title': self.title_entry.get_text(),
            'description': self.description_entry.get_text()
        }
        self._close()

    def _close(self, button=None):
        self.parent.unblur()
        self.close()

    def get_responses(self):
        return self.data


class SaveDialog(TemplateDialog):
    def __init__(self, widget, window):
        TemplateDialog.__init__(self, widget, window, _('Save').upper())


class ShareDialog(TemplateDialog):
    def __init__(self, widget, window):
        TemplateDialog.__init__(self, widget, window, _('Share').upper())
