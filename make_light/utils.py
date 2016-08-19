# utils.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import os
from gettext import _expand_lang

from kano.gtk3.kano_dialog import KanoDialog
from kano.utils import run_cmd
from make_light.paths import CHALLENGES_DIR, CHALLENGE_GROUPS


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


def get_challenges_path():
    """
    Construct the challenges path, first looking for any translation,
    and falling back to the default location.

    Returns:
        path (str) - the path to the challenges directory
    """

    challenges_path = CHALLENGES_DIR

    lang_dirs = get_language_dirs()

    for lang_dir in lang_dirs:
        path_candidate = os.path.join(CHALLENGES_DIR, 'locales', lang_dir, CHALLENGE_GROUPS)
        if os.path.isdir(path_candidate):
            challenges_path = path_candidate
            break

    return challenges_path


language_dirs = None

def get_language_dirs():
    """
    Get possible language directories to be searched for, based on 
    the environment variables: LANGUAGE, LC_ALL, LC_MESSAGES and LANG.
    The result is memoized for future use.

    This function is inspired by python gettext.py.

    Returns:
        dirs (array) - an array of language directories
    """

    # TODO: extract in kano-i18n?  This function is also used in Terminal Quest

    global language_dirs
    if language_dirs is not None:
        return language_dirs

    languages = []
    for envar in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
        val = os.environ.get(envar)
        if val:
            languages = val.split(':')
            break
    if 'C' in languages:
        languages.remove('C')

    # now normalize and expand the languages
    nelangs = []
    for lang in languages:
        for nelang in gettext._expand_lang(lang):
            if nelang not in nelangs:
                nelangs.append(nelang)

    language_dirs = nelangs
    return language_dirs


