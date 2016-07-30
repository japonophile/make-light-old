# ctl.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Controller functions to start, stop and check the status of the Powerup Kit
# connections


from kano.utils.hardware import has_min_performance, RPI_2_B_KEY, \
    get_board_property
from kano.logging import logger
from kano.network import is_internet
from kano.decorators import require_root

from powerup_network.network import is_ethernet_plugged, is_dnsmasq_running, \
    start_dnsmasq, stop_dnsmasq, set_fixed_ip, restore_ip_settings, \
    is_ethernet_ip


def status():
    ethernet_plugged = is_ethernet_plugged()
    logger.info('Internet connection is up: {}'.format(is_internet()))

    running = is_dnsmasq_running()
    if has_min_performance(get_board_property(RPI_2_B_KEY, 'performance')):
        if not ethernet_plugged:
            logger.info('Ethernet cable is not plugged in')
            return False
        else:
            logger.info('Ethernet cable is correctly plugged in')

        if not running:
            logger.warn(
                'dnsmasq not running - '
                'Please run "sudo powerup-network -u" to start networking'
            )
        else:
            logger.info('dnsmasq is up and running')

        logger.info('This is the Master Powerup Kit')
    else:
        logger.info('This is the Slave Powerup Kit')

    return running


@require_root()
def start():
    if not has_min_performance(get_board_property(RPI_2_B_KEY, 'performance')):
        logger.error('This is not at least a RaspberryPI 2 - aborting')
        return False

    if not is_ethernet_plugged():
        logger.info('Ethernet cable is not plugged in')
        return False
    else:
        if is_ethernet_ip():
            logger.info('Ethernet is connected to a router')
            return True

    if is_dnsmasq_running():
        logger.warn('networking is already running')
        return True

    if not set_fixed_ip():
        logger.error('Could not force a fixed IP address')
        return False

    if not start_dnsmasq():
        logger.error('Error installing dnsmasq')
        return False

    logger.info(
        'Powerup kit networking installed - please connect the ethernet cable'
    )
    return True


@require_root()
def stop():
    if not is_dnsmasq_running():
        return True

    # Firstly, stop the DHCP server to avoid it
    # from serving one to ourselves.
    if not stop_dnsmasq():
        return False

    # Then bring the Ethernet device back to client DHCP mode
    return restore_ip_settings()
