# available_boards.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Logic for discovering module definitions available for use

import os
import importlib

from make_light.paths import BOARDS_DIR

BOARD_MODULE_TEMPLATE = 'make_light.boards.available_boards.{board_name}.{board_type}'

PHYSICAL_BOARD = 'physical_board'
SIMULATION_BOARD = 'simulation_board'

def is_valid_board(board_path):
    required_files = [
        'simulation_board.py',
        'physical_board.py',
        'board.png',
        'board-mask.png'
    ]

    contents = os.listdir(board_path)

    for req_file in required_files:
        if req_file not in contents:
            return False

    return True

def get_board_object(board_path, board_type=SIMULATION_BOARD):
    board_module_name = board_path.split('/')[-1]

    board_module = importlib.import_module(
        BOARD_MODULE_TEMPLATE.format(
            board_name=board_module_name, board_type=board_type
        )
    )

    return board_module.Board

def get_board_metadata(board_path):
    sim_board = get_board_object(board_path, board_type=SIMULATION_BOARD)
    return {
        'name': sim_board.NAME,
        'board_image': os.path.join(board_path, 'board.png'),
        'simulation_board': sim_board,
        'physical_board': get_board_object(board_path,
                                           board_type=PHYSICAL_BOARD),
        'path': board_path,

    }

def get_available_boards():
    board_dir_contents = [
        os.path.join(BOARDS_DIR, f) for f in os.listdir(BOARDS_DIR)
    ]
    candidates = [d for d in board_dir_contents if os.path.isdir(d)]
    valid_board_paths = [board for board in candidates if is_valid_board(board)]

    valid_boards = [get_board_metadata(board) for board in valid_board_paths]

    return {board['name']: board for board in valid_boards}

AVAILABLE_BOARDS = get_available_boards()
