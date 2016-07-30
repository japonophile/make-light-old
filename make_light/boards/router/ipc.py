# ipc.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tools for IPC
# TODO: Move more IPC into here


from os import remove
from os.path import exists

from make_light.paths import SIM_PIPE

def remove_pipe():
    if exists(SIM_PIPE):
        remove(SIM_PIPE)
