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

if simulation:
    from make_light.boards.available_boards.led_speaker.simulation_board \
        import LEDSpeaker
    board = LEDSpeaker()
else:
    from make_light.boards.available_boards.led_speaker.physical_board import \
        LEDSpeakerPhysical
    board = LEDSpeakerPhysical()

light = board
light.clear()
light.reset_exports()
