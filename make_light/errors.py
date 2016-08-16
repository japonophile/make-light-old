# errors.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Standard Errors and Warning messages
# Errors with an error_code != 0 are FATAL and the app should exit with it
# Warnings are intended to be displayed with show_confirm_dialog
#
# NOTE: To prevent the dialog from stretching, \n has been used


ALREADY_RUNNING_ERROR = {
    'title': _('Make Light already running!'),
    'description': _('Another instance of Make Light is already running.'),
    'error_code': 1
}
NO_FRAMES_ERROR = {
    'title': _('Nothing to save!'),
    'description': _('If you would like to save your animation, first click MAKE to see'
                     '\n it in the Simulator.'),
    'error_code': 0
}
SIZE_REQ_ERROR = {
    'title': _('Animation too large!'),
    'description': _('Please try to trim the animation in the code to fewer frames.'),
    'error_code': 0
}
SAVE_EXISTS_ERROR = {
    'title': _('Save already exists!'),
    'description': _('You have already saved a creation with that title.'
                     '\n Please try a different one.'),
    'error_code': 0
}
RENAME_LIMIT_ERROR = {
    'title': _('Too many saves with the same title!'),
    'description': _('You have exceeded the limit of saves with the same title.'
                     '\n Please try a different one.'),
    'error_code': 0
}
UNEXPECTED_ERROR = {
    'title': _('Unexpected error occurred!'),
    'description': _('Unfortunately, this feature has encountered technical issues.'
                     '\n We might have already fixed it, so make sure to run Kano Updater'
                     '\n and try again.'),
    'error_code': 0
}
UNSUPPORTED_BOARD_ERROR = {
    'title': _('Unsupported Board!'),
    'description': _("Unfortunately, you attempted to change your hardware to a"
                     "\n board we don't support in this version of Make Light."
                     "\n Please try updating the app or report this issue."
                     ),
    'error_code': 0
}
NOT_SAVED_WARNING = {
    'title': _('You have not saved your work!'),
    'description': _('If you would like to keep your work, make sure to SAVE it!'
                     '\n You can continue working on your creations with a simple LOAD in Playground.'),
    'affirmative_button': _('Save now').upper(),
    'negative_button': _('Discard changes').upper(),
    'abort_button': _('Cancel').upper()
}
