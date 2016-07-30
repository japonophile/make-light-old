# challenge_icons.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


from os.path import join
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

from kano.gtk3.cursor import attach_cursor_events

from make_light.paths import ICONS_DIR


class ChallengesIconTemplate(Gtk.Button):
    ICON_WIDTH = 220
    ICON_HEIGHT = 250

    SCREENSHOT_WIDTH = 220
    SCREENSHOT_HEIGHT = 200

    INDICATOR_PATH = ICONS_DIR
    INDICATOR_W = 20
    INDICATOR_H = 20

    LABEL_PADDING = 10

    TICK_PB = Pixbuf.new_from_file_at_size(
        join(INDICATOR_PATH, 'success.png'), INDICATOR_W, INDICATOR_H
    )
    ARROW_PB = Pixbuf.new_from_file_at_size(
        join(INDICATOR_PATH, 'next.png'), INDICATOR_W, INDICATOR_H
    )
    LOCKED_PB = Pixbuf.new_from_file_at_size(
        join(INDICATOR_PATH, 'locked.png'), INDICATOR_W, INDICATOR_H
    )

    def __init__(self, challenge_like):
        Gtk.Button.__init__(self)
        attach_cursor_events(self)

        self.get_style_context().add_class('challenge-icon')
        self.set_size_request(self.ICON_WIDTH, self.ICON_HEIGHT)
        self.set_valign(Gtk.Align.START)

        self.challenge_like = challenge_like

        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self._box)

        img = self._create_image()
        self._box.pack_start(img, False, False, 0)

        label = self._create_label()
        self._box.pack_start(label, False, False, 0)

    def _create_image(self):
        pixbuf = Pixbuf.new_from_file_at_size(
            self.challenge_like.image_path,
            self.SCREENSHOT_WIDTH,
            self.SCREENSHOT_HEIGHT
        )

        return Gtk.Image.new_from_pixbuf(pixbuf)

    def _create_label(self):
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label_box.set_size_request(
            -1, self.ICON_HEIGHT - self.SCREENSHOT_HEIGHT
        )

        label = Gtk.Label(self.challenge_like.title)
        label.set_valign(Gtk.Align.CENTER)
        label.set_margin_left(self.LABEL_PADDING)
        label_box.pack_start(label, False, False, 0)

        if self.challenge_like.locked:
            css_class = 'locked'
            img_pixbuf = self.LOCKED_PB
        elif self.challenge_like.completed:
            css_class = 'completed'
            img_pixbuf = self.TICK_PB
        else:
            css_class = 'current'
            img_pixbuf = self.ARROW_PB

        self.get_style_context().add_class(css_class)

        icon = Gtk.Image.new_from_pixbuf(img_pixbuf)
        icon.set_valign(Gtk.Align.CENTER)
        icon.set_margin_right(self.LABEL_PADDING)
        label_box.pack_end(icon, False, False, 0)

        return label_box


class ChallengeIcon(ChallengesIconTemplate):
    ICON_WIDTH = 180
    ICON_HEIGHT = 230

    SCREENSHOT_WIDTH = 180
    SCREENSHOT_HEIGHT = 180


class ChallengeGroup(ChallengesIconTemplate):
    ICON_WIDTH = 480
    SCREENSHOT_WIDTH = 480

