# aliases.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# aliases for common constants


def timenow():
    """Returns current time as a string in a typical format

    :returns: formatted string
    :rtype: str
    """
    import time
    return time.strftime('%H:%M:%S')

on = True
On = True
ON = True

off = False
Off = False
OFF = False

true = True
false = False
