# dbus_interface.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Create the bus and interface names

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

BUS_ID_LIST = ['me', 'kano', 'make_light']

BUS_NAME_STR = '.'.join(BUS_ID_LIST)
BUS_INTERFACE = '{}.Actions'.format(BUS_NAME_STR)
OBJECT_PATH = '/{}'.format('/'.join(BUS_ID_LIST))

DBUS_LOOP = DBusGMainLoop(set_as_default=True)

SESSION_BUS = dbus.SessionBus()
BUS_NAME = dbus.service.BusName(BUS_NAME_STR, bus=SESSION_BUS)
