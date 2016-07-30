# config.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Configuration constants for Powerup Kit connectivity


# postinst / postrm will keep a safeguard copy of the original settings
INTERFACES_FILE = '/etc/network/interfaces'
INTERFACES_BACKUP_FILE = '/etc/network/interfaces-backup'

# Index in the iptables chain where our rule will sit
IPTABLES_RULE_NUMBER = 1

# Configuration to set a static IP address to Ethernet on the Master Kit
ETH0_IP_ADDRESS = '169.254.0.1'
ETH0_CONFIGURATION = '''
# interfaces
auto lo
iface lo inet loopback

allow-hotplug eth0
iface eth0 inet static
  address {}
  netmask 255.255.255.0
  network 169.254.0.0
  broadcast 169.254.0.255

allow-hotplug wlan0
iface wlan0 inet manual

'''.format(ETH0_IP_ADDRESS)
