# challenge_progress.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The container showing the instructions.


from gi.repository import Gtk, GObject, Pango

from make_light.logic import Challenges
from make_light.gtk3.components.page_control import PageControl
from make_light.gtk3.dimensions import WINDOW_PADDING, CHALLENGE_PROGRESS_HEIGHT


class ChallengeProgress(Gtk.Box):

    __gsignals__ = {
        'challenge-done': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, challenge, step=0):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        # We track whether the user has completed the current challenge
        # and if not, how many steps they have completed
        # To determine how many steps they are allowed to see
        self.challenge = challenge
        self.step = step

        # container styling
        self.set_size_request(-1, CHALLENGE_PROGRESS_HEIGHT)
        self.set_margin_left(WINDOW_PADDING)
        self.set_margin_right(WINDOW_PADDING)
        self.get_style_context().add_class('challenge-progress-header')

        # the layout of the component
        top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        top_box.set_margin_top(15)
        top_box.set_margin_left(20)
        # top_box.set_margin_right(20)
        top_box.set_halign(Gtk.Align.FILL)
        self._populate_top_box(top_box)
        self.pack_start(top_box, False, False, 0)

        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        bottom_box.set_margin_top(30)
        bottom_box.set_margin_left(20)
        bottom_box.set_margin_right(20)
        bottom_box.set_halign(Gtk.Align.FILL)
        self._populate_bottom_box(bottom_box)
        self.pack_start(bottom_box, False, False, 0)

        # Max step the user has completed
        self.max_step = step
        if self.challenge.completed:
            self.max_step = len(self.challenge.content)

        self.total_challenges = len(
            Challenges.get_instance()[challenge.group_id]
        )

        # Slight inconsistancy here - first challenge is 1, but the
        # first step is 0
        self.get_tutorial(self.challenge)

    def _populate_top_box(self, top_box):
        self.tutorial_title = Gtk.Label()
        self.tutorial_title.get_style_context().add_class('challenge-progress-title')
        top_box.pack_start(self.tutorial_title, False, False, 0)

        # Initialise with the total number of steps in the tutorial
        # The rest of the defaults are fine.
        # box = Gtk.Box()
        self.page_control = PageControl(
            num_of_pages=len(self.challenge.content),
            initial_limit_steps=1
        )
        self.page_control.connect(
            "back-button-clicked",
            self._get_tutorial_wrapper,
            False
        )
        self.page_control.connect(
            "next-button-clicked",
            self._get_tutorial_wrapper,
            True
        )
        # box.pack_start(self.page_control, False, False, 0)
        self.page_control.set(1, 0.5, 0, 0)  # xalign, yalign, xscale, yscale
        top_box.pack_start(self.page_control, True, True, 0)

    def _populate_bottom_box(self, bottom_box):
        # The tutorial text widget, where the steps are explained
        self.tutorial_text = Gtk.Label()
        self.tutorial_text.get_style_context().add_class('challenge-progress-hint')
        self.tutorial_text.set_line_wrap(True)
        self.tutorial_text.set_max_width_chars(50)
        self.tutorial_text.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.tutorial_text.set_halign(Gtk.Align.START)
        bottom_box.pack_start(self.tutorial_text, False, False, 0)

        spacer = Gtk.Label()  # meh
        spacer.set_hexpand(True)
        bottom_box.pack_start(spacer, True, True, 0)

    def _get_tutorial_wrapper(self, widget, next_step=True):
        """
        Get the next tutorial and display it on the dialog
        If there are no more steps, show a "Done!" button
        """

        # Handle the 'DONE' case
        # if next_step and self.step == self.challenge_steps - 1:
        #     self.emit('challenge-done')
        #     return

        if next_step:
            self.step += 1
            self.max_step = max(self.step, self.max_step)

            if self.step == self.challenge_steps - 1:
                self.emit('challenge-done')
        else:
            self.step -= 1

        # Have we completed this challenge?
        # Currently the challenge is considered complete on the penultimate step
        # The last one is 'press MAKE' and advice about what to do next.
        if next_step and self.step == self.challenge_steps - 1:
            self.challenge.completed = True
        self.get_tutorial(self.challenge, self.step)

    def validate_code(self, code):
        """
        Validate that the code matches the regexps for the current step.

        We also calculate the number of matching regexps, so it is possible to
        wind back the tutorial steps if earlier lines are broken, but don't
        do this yet.
        """

        # We operate by iterating over lines, at each point having a current
        # regexp to check (which may be None)
        # We increment if the regexp matches AND there is a later line
        # (ie, the user pressed enter).

        re_list = self.re_list[:]

        if len(re_list):
            (curr_line, curr_re) = re_list.pop(0)
        else:
            curr_re = None
            curr_line = None

        steps_matched = 0
        for (index, line) in enumerate(code):
            if line.isspace() or line == '':
                continue

            if curr_re is not None:
                if curr_re.match(line):
                    if index + 1 < len(code):
                        steps_matched += 1
                    if len(re_list):
                        (curr_line, curr_re) = re_list.pop(0)
                    else:
                        curr_re = None
                else:
                    break
        # return true if all steps match and ther
        return steps_matched == len(self.re_list)

    def get_tutorial(self, challenge, step=0):
        """
        Collect data from the challenge tutorial and change title
        """
        self.step = step
        self.challenge = challenge

        title = challenge.title
        content = challenge.content
        self.challenge_steps = len(content)
        step_text = challenge.content[step]["text"]

        # this is the code line required to complete this step
        self.re_list = [challenge.get_re(i) for i in xrange(step + 1)]

        # update tutorial title and text contents
        self.tutorial_title.set_text(title)

        # set_markup will parse SGML embed the text support the markup language
        # as documented here:
        # http://www.pygtk.org/pygtk2reference/pango-markup-language.html
        self.tutorial_text.set_markup(step_text)

        self.page_control.set_appearence_from_page_number(
            step + 1, self.challenge_steps, self.max_step + 1
        )

    def on_code_changed(self, myCodeEdit, ignored):
        """
        The purpose of this function is to detect when the user
        has entered a code line as requested by the challenge tips
        (tag "code" in the Yaml file)

        This function is called on each key press, be as fast as you can.
        """

        # FIXME: For no obvious reason, we are passed the codeEdit object twice.
        # We ignore the second one

        # get last line of code, ignoring empty lines
        lines = myCodeEdit.get_code().split('\n')
        if self.validate_code(lines):
            # Jump to the next challenge step if user typed expected code
            self._get_tutorial_wrapper(None, True)
