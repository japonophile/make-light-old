# network.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Raw functions to control network interfaces for the Powerup Kit


import os
import shutil

from kano.logging import logger
from kano.decorators import require_root

from powerup_network.config import ETH0_IP_ADDRESS, ETH0_CONFIGURATION, \
    INTERFACES_FILE, INTERFACES_BACKUP_FILE, IPTABLES_RULE_NUMBER


@require_root()
def set_fixed_ip():
    logger.info('Setting Ethernet fixed IP address: {}'.format(ETH0_IP_ADDRESS))
    with open(INTERFACES_FILE, 'w') as f:
        f.writelines(ETH0_CONFIGURATION)

    rc = os.system('/sbin/ifdown eth0; /sbin/ifup eth0 > /dev/null 2>&1')
    return rc == 0


@require_root()
def restore_ip_settings():
    if os.path.isfile(INTERFACES_BACKUP_FILE):
        logger.info('Restoring original network interface settings')
        shutil.copy(INTERFACES_BACKUP_FILE, INTERFACES_FILE)

        # We are removing the IP from the Ethernet. It should now act as a
        # client and request a DHCP lease from the network.
        rc = os.system('ifconfig eth0 0.0.0.0')
        return rc == 0

    return False


@require_root()
def dnsmasq_command(command):
    rc = os.system('/etc/init.d/dnsmasq {}'.format(command))
    return rc == 0


@require_root()
def start_dnsmasq():
    # TODO: Use return values from commands to verify success

    # Enable routing between ethernet and wireless, and IP masquerading
    os.system('/sbin/sysctl -w net.ipv4.ip_forward=1')

    # Use "iptables -nvL -t nat" to list all the rules in the chains
    os.system(
        '/sbin/iptables -t nat -I POSTROUTING {} -o wlan0 -j MASQUERADE '
        '-m comment --comment "PowerUp Kit eth to wlan routing"'
        .format(IPTABLES_RULE_NUMBER)
    )

    return dnsmasq_command('start')


@require_root()
def stop_dnsmasq():
    # TODO: Use return values from commands to verify success

    # Enable routing between ethernet and wireless, and IP masquerading
    os.system('/sbin/sysctl -w net.ipv4.ip_forward=0')
    os.system(
        'iptables -t nat -D POSTROUTING {}'.format(IPTABLES_RULE_NUMBER)
    )
    return dnsmasq_command('stop')


def is_dnsmasq_running():
    try:
        dnsmasq_pid = open('/var/run/dnsmasq/dnsmasq.pid', 'r').read().strip()
        running = os.path.exists('/proc/{}'.format(dnsmasq_pid))
    except Exception:
        running = False

    return running


def is_ethernet_plugged(device='eth0'):
    '''
    returns True if the Ethernet network cable is physically plugged in
    '''
    eth_link = os.popen('ifplugstatus {}'.format(device)).read().strip()
    return eth_link in ('{}: link beat detected'.format(device))


def is_ethernet_ip(device='eth0'):
    '''
    Returns the network device IP address, if not configured by powerup-network.
    If is_ethernet_plugged also returns True, it means you are connected to a
    router.
    '''
    try:
        cmdline = "ip addr show {} | grep \"inet \"".format(device)
        output = os.popen(cmdline).read().strip()
        ip_address = output.split()[1]
        if len(ip_address) and \
                not ip_address.startswith('0.0.0.0') and \
                not ip_address.startswith(ETH0_IP_ADDRESS):
            return ip_address
    except Exception:
        return None
