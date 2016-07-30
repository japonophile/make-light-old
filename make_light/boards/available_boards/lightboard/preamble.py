import os

debug = False
simulation = False
token = ''

if 'POWERUP_DEBUG' in os.environ:
    simulation = True
    debug = True
elif 'POWERUP_TEST' in os.environ:
    simulation = True
elif 'POWERUP_MAKE' in os.environ:
    device = os.environ['POWERUP_MAKE']

if 'API_TOKEN' in os.environ:
    token = os.environ['API_TOKEN']

if simulation:
    from make_light.boards.available_boards.lightboard.simulation_board import \
        KanoLightBoard
    board = KanoLightBoard(debug=debug)
else:
    from make_light.boards.available_boards.lightboard.physical_board import \
        KanoLightBoardPhysical
    board = KanoLightBoardPhysical()

light = board
light.clear()
light.reset_exports()
