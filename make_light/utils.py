# utils.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


from os import getpid

from kano.gtk3.kano_dialog import KanoDialog
from kano.utils import run_cmd


AFFIRMATIVE_ACTION = 1
NEGATIVE_ACTION = 0
ABORT_ACTION = -1


def other_similar_process_running():
    result, d1, d2 = run_cmd("pgrep -f '^python.*[^:]make-light\W?$'")
    pids = [int(pid) for pid in result.strip().splitlines()
            if int(pid) != getpid()]
    return pids


def show_error_dialog(error, window=None):
    """
    This can be used to display an error from errors.py
    """
    error_dialog = KanoDialog(
        title_text=error['title'],
        description_text=error['description'],
        button_dict={
            'OK': {
                'label': 'OK',
                'color': 'red'
            }
        },
        parent_window=window,
        hide_from_taskbar=True
    )
    error_dialog.run()


def show_confirm_dialog(message, window=None):
    """
    This can be used to display a warning from errors.py
    It returns AFFIRMATIVE_ACTION, NEGATIVE_ACTION or ABORT_ACTION
    corresponding to the users option
    """

    dialog = KanoDialog(
        title_text=message['title'],
        description_text=message['description'],
        button_dict={
            message['affirmative_button']: {
                'color': 'green',
                'return_value': AFFIRMATIVE_ACTION
            },
            message['negative_button']: {
                'color': 'red',
                'return_value': NEGATIVE_ACTION
            },
            message['abort_button']: {
                'color': 'red',
                'return_value': ABORT_ACTION
            }
        },
        parent_window=window,
        hide_from_taskbar=True
    )
    return_value = dialog.run()

    return return_value
