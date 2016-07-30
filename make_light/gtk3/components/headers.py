# headers.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


from gi.repository import Gtk, GObject

from kano.gtk3.cursor import attach_cursor_events

from make_light.gtk3.components.challenge_progress import ChallengeProgress
from make_light.gtk3.dimensions import VIEW_WIDTH, HEADER_BUTTON_HEIGHT, \
    HEADER_BUTTON_WIDTH, WINDOW_PADDING


class HeaderTemplate(Gtk.Box):
    """
    """

    __gsignals__ = {
        'back-button-pressed': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'next-button-pressed': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
    }

    def __init__(self, middle_component):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        # container styling
        self.set_size_request(VIEW_WIDTH, -1)
        self.set_halign(Gtk.Align.CENTER)  # center component in window
        self.set_margin_top(WINDOW_PADDING)
        self.get_style_context().add_class('light-ide-header')

        # the BACK button
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        button_box.set_valign(Gtk.Align.FILL)
        self.back_button = Gtk.Button('<   ' + 'Back'.upper())  # TODO: i18n
        self.back_button.connect('clicked', self._back_button_pressed)
        self.back_button.get_style_context().add_class('header-back-button')
        self.back_button.set_size_request(HEADER_BUTTON_WIDTH, HEADER_BUTTON_HEIGHT)
        self.back_button.set_margin_left(WINDOW_PADDING)
        attach_cursor_events(self.back_button)
        button_box.pack_start(self.back_button, False, False, 0)
        spacer = Gtk.Label()  # meh
        button_box.pack_start(spacer, True, True, 0)
        self.pack_start(button_box, False, False, 0)

        # the middle component in the header is set by each individual header
        self.pack_start(middle_component, True, True, 0)

        # the NEXT button
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        button_box.set_valign(Gtk.Align.FILL)
        self.next_button = Gtk.Button('Next'.upper() + '   >')  # TODO: i18n
        self.next_signal_id = self.next_button.connect(
            'clicked',
            self._next_button_pressed
        )
        self.next_button.get_style_context().add_class('header-next-button')
        self.next_button.set_size_request(HEADER_BUTTON_WIDTH, HEADER_BUTTON_HEIGHT)
        self.next_button.set_margin_right(WINDOW_PADDING)
        attach_cursor_events(self.next_button)
        button_box.pack_start(self.next_button, False, False, 0)
        spacer = Gtk.Label()  # meh
        button_box.pack_start(spacer, True, True, 0)
        self.pack_start(button_box, False, False, 0)

    def set_next_button_sensitivity(self, is_sensitive):
        self.next_button.set_sensitive(is_sensitive)

    def _back_button_pressed(self, button=None):
        self.emit('back-button-pressed')

    def _next_button_pressed(self, button=None):
        self.emit('next-button-pressed')


class ListHeader(HeaderTemplate):
    """
    This header is used by GroupListView and ChallengeListView
    """

    def __init__(self, white_text='', orange_text='', bottom_text=''):
        # compose the middle component for the HeaderTemplate
        middle_component = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # the component layout is handled by a grid with a top box
        top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        top_box.set_margin_top(4)
        top_box.set_halign(Gtk.Align.CENTER)
        middle_component.pack_start(top_box, False, False, 0)

        # and a bottom box
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        bottom_box.set_margin_top(4)
        bottom_box.set_halign(Gtk.Align.CENTER)
        middle_component.pack_start(bottom_box, False, False, 0)

        # adding the three types of labels to the boxes, first the white
        white_label = Gtk.Label(white_text)
        white_label.get_style_context().add_class('header-white-label')
        top_box.pack_start(white_label, False, False, 0)

        # the orange label
        orange_label = Gtk.Label(orange_text)
        orange_label.get_style_context().add_class('header-orange-label')
        orange_label.set_margin_left(10)
        top_box.pack_start(orange_label, False, False, 0)

        # and the gray label
        bottom_label = Gtk.Label(bottom_text)
        bottom_label.get_style_context().add_class('header-bottom-label')
        bottom_box.pack_start(bottom_label, False, False, 0)

        # now pass the middle component to the HeaderTemplate
        HeaderTemplate.__init__(self, middle_component)
        self.set_next_button_sensitivity(False)  # disable the NEXT button


class ChallengeHeader(HeaderTemplate):
    """
    This header is used by ChallengeView
    """

    __gsignals__ = {
        'challenge-done': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'done-button-pressed': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
    }

    def __init__(self, challenge, is_final=False):
        self.challenge_progress = ChallengeProgress(challenge)
        self.challenge_progress.connect(
            'challenge-done',
            self._on_challenge_done
        )

        self.is_final = is_final

        # now pass the middle component to the HeaderTemplate
        HeaderTemplate.__init__(self, self.challenge_progress)
        if self.is_final:
            self._replace_next_with_done()

        self.set_next_button_sensitivity(False)  # disable the NEXT button
        self.is_challenge_done = False

    def _on_challenge_done(self, widget=None):
        self.is_challenge_done = True

    def on_make(self, button=None):
        if not self.is_challenge_done:
            return

        self.emit('challenge-done')
        self.set_next_button_sensitivity(True)

        next_label = 'DONE' if self.is_final else 'NEXT >'
        complete_text = '''
            Click <span foreground='#ffffff'
                        background='#ff842a'
                        face='monospace'
                        size='smaller'
                        font-weight='bold'
            > {next_label} </span> to continue
        '''.format(next_label=next_label).strip()
        self.challenge_progress.tutorial_text.set_markup(complete_text)

    def on_code_changed(self, code_edit, ignored):
        self.challenge_progress.on_code_changed(code_edit, ignored)

    def _done_button_pressed(self, button=None):
        self.emit('done-button-pressed')

    def _replace_next_with_done(self):
        self.next_button.set_label('Done'.upper())
        self.next_button.disconnect(self.next_signal_id)
        self.next_signal_id = self.next_button.connect(
            'clicked',
            self._done_button_pressed
        )


class PlaygroundHeader(HeaderTemplate):
    """
    This header is used by PlaygroundView
    """

    def __init__(self):
        # compose the middle component for the HeaderTemplate
        middle_component = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        title = Gtk.Label('Playground')
        title.get_style_context().add_class('header-white-label')
        middle_component.pack_start(title, True, True, 0)

        # now pass the middle component to the HeaderTemplate
        HeaderTemplate.__init__(self, middle_component)
        self.set_next_button_sensitivity(False)  # disable the NEXT button
