# welcome_window.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Displays the first screen, explaining a sequence of tips paged with a Next
# button. A Close button allows to quit the app.


import os

from gi.repository import Gtk

from make_light.gtk3.components.page_control import PageControl
from make_light.paths import IMAGES_DIR

from kano.gtk3.application_window import ApplicationWindow


# Title and descriptions of the tips section at the bottom, linked to Next and
# Previous buttons
tips = [
    {
        'title': 'Welcome to Make Light',
        'image': 'Welcome1.png',
        'description': 'Turn on your lights. Make your kit flicker to life.'
    },
    {
        'title': 'Endless Possibilities',
        'image': 'Welcome2.png',
        'description': 'Pick a coding challenge. Learn to do all sorts of exciting things with your LED lights'
    },
    {
        'title': 'Turn Code Into Light',
        'image': 'Welcome3.png',
        'description': 'Complete challenges by typing computer code and clicking on the Make button'
    }
]


class WelcomeWindow(ApplicationWindow):

    def __init__(self):

        self.title = "Make Light"
        self.step = 1

        # On dialog termination, this flag will say wether to continue or quit
        # the app from whichever button has been selected from the tips flow.
        self.buttons_quit_continue = ('CLOSE', 'START')
        self.continue_app = True

        ApplicationWindow.__init__(self, self.title, -1, -1)

        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)

        # Grab the first image of the presentation
        image_file = os.path.join(IMAGES_DIR, tips[self.step - 1]['image'])
        self.half_image_box = Gtk.Image.new_from_file(image_file)
        self.half_image_box.get_style_context().add_class('top_image')

        # Also the title and description labels
        self.tips_title = Gtk.Label(tips[self.step - 1]['title'])
        self.tips_title.get_style_context().add_class('tip_title')

        self.tips_description = Gtk.Label(tips[self.step - 1]['description'])
        self.tips_description.get_style_context().add_class('tip_description')
        self.tips_description.set_max_width_chars(35)
        self.tips_description.set_line_wrap(True)
        self.tips_description.set_justify(Gtk.Justification.CENTER)
        self.tips_description.set_halign(Gtk.Align.CENTER)
        self.tips_description.set_valign(Gtk.Align.CENTER)
        self.tips_description.set_size_request(-1, 40)

        # Put it all together inside the window
        self.create_window_layout()

    def create_window_layout(self):
        '''
        Rearranges all controls inside the window, wrapped in a Gtk.Box
        '''

        # The box that holds the half-top image, and the tips section below.
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # tips section will sit below the image
        num_of_pages = 3
        self.page_control = PageControl(
            num_of_pages=num_of_pages,
            quit_text=self.buttons_quit_continue[0],
            continue_text=self.buttons_quit_continue[1]
        )
        self.page_control.set_margin_top(10)
        self.page_control.set_margin_bottom(20)
        self.page_control.connect(
            "back-button-clicked",
            self.get_tutorial_wrapper,
            False
        )
        self.page_control.connect(
            "next-button-clicked",
            self.get_tutorial_wrapper,
            True
        )

        self.vbox.set_margin_top(0)
        self.vbox.set_margin_left(0)
        self.vbox.set_margin_right(0)
        self.vbox.set_margin_bottom(0)

        self.vbox.pack_start(self.half_image_box, True, False, 0)
        self.vbox.pack_start(self.tips_title, True, False, 0)
        self.vbox.pack_start(self.tips_description, True, False, 0)
        self.vbox.pack_end(self.page_control, False, False, 0)

        self.set_main_widget(self.vbox)
        self.show_all()

    def get_tutorial_wrapper(self, widget, next_step=True):
        '''
        This method is called for each click on either the Next or Previous
        buttons
        '''

        if self.step == 1 and not next_step:
            self.continue_app = False
            self.destroy()
            return

        if self.step == 3 and next_step:
            self.continue_app = True
            self.destroy()
            return

        if next_step:
            self.step += 1
        else:
            self.step -= 1

        # update the tip section title, description and top image
        self.tips_title.set_text(tips[self.step - 1]['title'])
        self.tips_description.set_text(tips[self.step - 1]['description'])

        # update the image along with it
        image_file = os.path.join(IMAGES_DIR, tips[self.step - 1]['image'])
        self.half_image_box = Gtk.Image.new_from_file(image_file)
        self.half_image_box.get_style_context().add_class('top_image')

        # Rearrange all the widgets in the window
        self.remove_main_widget()
        self.create_window_layout()

        # Update the scrolling buttons and the current page radio button
        self.page_control.set_appearence_from_page_number(self.step, 3)
