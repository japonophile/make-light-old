# page_control.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This creates a widget that you can use to control the screen


import os

from gi.repository import Gtk, GObject

from make_light.gtk3.components.gtk_hider import GtkHider
from make_light.paths import CSS_DIR

from kano.gtk3.buttons import OrangeButton
from kano.gtk3.cursor import attach_cursor_events
from kano.gtk3.apply_styles import apply_styling_to_screen


class PageControl(Gtk.Alignment):

    __gsignals__ = {
        'back-button-clicked': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'next-button-clicked': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self,
                 num_of_pages=3,
                 selected_page=1,
                 back_text="BACK",
                 next_text="NEXT",
                 initial_limit_steps=None,
                 quit_text=None,
                 continue_text=None):

        self.quit_text = quit_text
        self.continue_text = continue_text

        self.back_text = back_text
        self.next_text = next_text

        Gtk.Alignment.__init__(self, xalign=0.5, xscale=0, yscale=0, yalign=0.5)
        self.num_of_pages = num_of_pages
        self.selected = selected_page
        apply_styling_to_screen(os.path.join(CSS_DIR, 'powerup.css'))

        self._box = Gtk.Box()
        self.add(self._box)

        self._back_button = OrangeButton(self.back_text)
        self._back_button.connect("clicked", self.back_button_clicked)
        attach_cursor_events(self._back_button)

        self._next_button = OrangeButton(self.next_text)
        self._next_button.connect("clicked", self.next_button_clicked)
        attach_cursor_events(self._next_button)

        self._back_hider = GtkHider(self._back_button)
        self._next_hider = GtkHider(self._next_button)

        self.dot_box = Gtk.Box()
        self._box.pack_start(self._back_hider, False, False, 40)
        self._box.pack_start(self.dot_box, False, False, 0)
        self._box.pack_start(self._next_hider, False, False, 40)
        self.set_appearence_from_page_number(self.selected, self.num_of_pages,
                                             limit_steps=initial_limit_steps)
        self.show_all()

    @property
    def back_button(self):
        return self._back_button

    @property
    def next_button(self):
        return self._next_button

    # TODO: these are expanding to fill the parent container.
    def set_appearence_from_page_number(self, page_num, max_steps,
                                        limit_steps=None):
        """Fill the dot box with orange and grey dots
        """
        self.num_of_pages = max_steps
        if limit_steps is None:
            limit_steps = max_steps

        # Only change the packing if the page number is valid.
        if page_num >= 1 and \
                page_num <= self.num_of_pages:

            for dot in self.dot_box.get_children():
                self.dot_box.remove(dot)

            self.selected = page_num

            for i in range(self.selected - 1):
                dot = self._create_unselected_dot()
                self.dot_box.pack_start(dot, False, False, 0)

            dot = self._create_selected_dot()
            self.dot_box.pack_start(dot, False, False, 0)

            for i in range(self.selected, self.num_of_pages):
                dot = self._create_unselected_dot()
                self.dot_box.pack_start(dot, False, False, 0)

            # In quit_and_continue mode, the buttons are not disabled,
            # but instead, replaced by the string tuples (left, right)
            # to allow for custom actions (quit and continue from dialog, for example)

            if self.selected == 1:
                if self.quit_text:
                    self._back_button.set_label(self.quit_text)
                else:
                    self.disable_back()

            else:
                # We move away from the back button
                self._back_button.set_label(self.back_text)
                self.enable_back()

            # we reached the end to the right
            if self.selected == self.num_of_pages:
                if self.continue_text:
                    self._next_button.set_label(self.continue_text)
                    self.enable_next()
                else:
                    self.disable_next()

            else:
                self._next_button.set_label(self.next_text)

                # If the number of steps is being limited
                # (eg, to prevent looking ahead)
                # disable the next button.
                if self.selected < limit_steps:
                    self.enable_next()
                else:
                    self.disable_next()

            self.show_all()

    def _create_dot(self):
        dot = Gtk.EventBox()
        dot.get_style_context().add_class("dot")
        return dot

    def _create_selected_dot(self):
        dot = self._create_dot()
        dot = self._make_dot_selected(dot)
        return dot

    def _create_unselected_dot(self):
        dot = self._create_dot()
        dot = self._make_dot_unselected(dot)
        return dot

    def _get_dot_by_page_num(self, page_num):
        return self.dot_box.get_children()[page_num]

    def _make_dot_unselected(self, dot):
        """Produce an unselected grey spot
        """
        dot.get_style_context().remove_class("selected")
        dot.get_style_context().add_class("unselected")
        dot.set_size_request(6, 6)
        dot.set_margin_left(5)
        dot.set_margin_right(5)
        dot.set_margin_top(15)
        dot.set_margin_bottom(15)

        # May not be necessary to return dot
        return dot

    def _make_dot_selected(self, dot):
        """Produce a selected orange dot
        """
        dot.get_style_context().add_class("selected")
        dot.get_style_context().remove_class("unselected")
        dot.set_size_request(10, 10)
        dot.set_margin_left(3)
        dot.set_margin_right(3)
        dot.set_margin_top(13)
        dot.set_margin_bottom(13)

        # May not be necessary to return dot
        return dot

    # These give external windows a way of knowing when these buttons have been
    # clicked, without mixing up the classes
    def back_button_clicked(self, widget):
        self.emit('back-button-clicked')
        # automatically change how the page control looks?

    def next_button_clicked(self, widget):
        self.emit('next-button-clicked')

    def enable_next(self):
        self._next_button.set_sensitive(True)
        self._next_hider.set_hidden(False)

    def enable_back(self):
        self._back_button.set_sensitive(True)
        self._back_hider.set_hidden(False)

    def disable_next(self):
        self._next_button.set_sensitive(False)
        self._next_hider.set_hidden(True)

    def disable_back(self):
        self._back_button.set_sensitive(False)
        self._back_hider.set_hidden(True)
