# paths.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Includes all the necessary paths for make light challenges


import stat

from os import chmod, mkfifo
from os.path import join, abspath, dirname, expanduser, exists

from kano.utils import ensure_dir, get_home_by_username, get_user_unsudoed, \
    chown_path
from kano.logging import logger
from kano_content.api import ContentManager


def get_paths_from_content():
    ret_list = []
    cm = ContentManager.from_local()
    for k in cm.list_local_objects(spec='make-light-groups'):
        ret_list.append(k.get_data('added_group').get_dir())
    return ret_list

# This is the default install path for our config stuff
BASE_DIR = "/usr/share/make-light"
LOCAL_DIR = abspath(join(dirname(__file__), '..'))
if not LOCAL_DIR.startswith('/usr'):
    BASE_DIR = LOCAL_DIR

HOME_DIR = get_home_by_username(get_user_unsudoed())

# RPi1 local user folder
POWERUP_LOCAL_DIRNAME = '.powerup'
POWERUP_LOCAL_PATH = expanduser(join('~', POWERUP_LOCAL_DIRNAME))

MEDIA_DIR = join(BASE_DIR, 'media')
CHALLENGE_GROUPS = 'challenge_groups'
CHALLENGES_DIR = join(BASE_DIR, CHALLENGE_GROUPS)
TEMP_DIR = join('/tmp', 'make-light', get_user_unsudoed())
SAVE_DIR = join(HOME_DIR, 'Light-content')

# resources paths - images, css, fonts, etc.
IMAGES_DIR = join(MEDIA_DIR, 'images')
FONTS_DIR = join(MEDIA_DIR, 'fonts')
CSS_DIR = join(MEDIA_DIR, 'css')
ICONS_DIR = join(IMAGES_DIR, 'icons')

# challenges assets
CHALLENGE_ASSET_DIR = join(IMAGES_DIR, 'challenges')
CHALLENGE_GROUP_ASSET_DIR = join(IMAGES_DIR, CHALLENGE_GROUPS)
INDEX_FILE_NAME = "index.json"
CHALLENGE_FILES_FMT = "{}.json"

ADDITIONAL_CHALLENGE_GROUPS = get_paths_from_content()

# gif animation temp processing paths
GIF_FRAMES_DIR = join(TEMP_DIR, 'frames')
GIF_DIR = join(TEMP_DIR, 'gif')
GIF_FILE_NAME = 'make-light.gif'


# save / share / load extensions
CODE_FILE_EXTENSION = 'lightcode'
SHARE_INFO_FILE_EXTENSION = 'json'
ANIMATION_FILE_EXTENSION = 'gif'

# kano content paths
CO_CHAL_GROUP_COVER_FMT = join('..', 'group_cover', '{id_str}.png')
CO_CHAL_COVER_FMT = join('..', 'challenge_covers', '{id_str}.png')


# Simulator Pipe
SIM_PIPE = join(TEMP_DIR, 'make-light-simulator.pipe')

# create the TEMP and LOCAL folders
ensure_dir(TEMP_DIR)
chown_path(TEMP_DIR)
ensure_dir(SAVE_DIR)
chown_path(SAVE_DIR)

# making sure the permissions on the temp folder are multi-user permissive
try:
    chmod(join(TEMP_DIR, '..'),
          stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
          stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
          stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)
except OSError:
    logger.warn(
        "Couldn't expand temp dir perms due to perm error, ironically"
    )

if not exists(SIM_PIPE):
    mkfifo(SIM_PIPE)
    chown_path(SIM_PIPE)

# POWERUP RPi1 local paths
if not exists(FONTS_DIR):
    FONTS_DIR = join(POWERUP_LOCAL_PATH, 'fonts')


PACKAGE_PATH = dirname(__file__)
BOARDS_ROOT_DIR = join(PACKAGE_PATH, 'boards')
BOARDS_BASE_DIR = join(BOARDS_ROOT_DIR, 'base')
BOARDS_DIR = join(BOARDS_ROOT_DIR, 'available_boards')
