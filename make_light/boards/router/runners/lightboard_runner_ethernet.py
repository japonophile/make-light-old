# lightboard_runner_ethernet.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Runs commands on remote Pi through ethernet

import os
import time
import os.path
import threading
import subprocess
from gi.repository import GObject

from kano_profile import tracker
from kano.logging import logger
from kano.utils import write_file_contents, read_file_contents, chown_path

from make_light.boards.router.runners.lightboard_runner import LightBoardRunner
from make_light import lib_version
from make_light.paths import POWERUP_LOCAL_PATH, POWERUP_LOCAL_DIRNAME, \
    FONTS_DIR


class LightBoardRunnerEthernet(LightBoardRunner):
    ssh_key_file = os.path.expanduser('~/.ssh/powerup.rsa')
    lib_version_file = os.path.join(POWERUP_LOCAL_PATH, 'written_lib')
    ssh_options = '-oLogLevel=quiet -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no -oConnectTimeout=5'
    ssh_address = 'powerup@powerup.local'

    def __init__(self, board):
        LightBoardRunner.__init__(self, board)
        self.thread_continue = True
        thread = threading.Thread(target=self.thr_powerup_heartbeat)
        thread.daemon = True
        thread.start()

    def thr_powerup_heartbeat(self):
        """
        Thread keeps track of LED kit connectivity and updates status message
        on main screen
        """
        detected = False
        setup_complete = False

        while self.thread_continue:
            success = not os.system('ping -c 1 powerup.local >/dev/null')
            if success and not self._available:
                if not detected:
                    detected = True
                    GObject.idle_add(self.emit, "powerup-status", detected,
                                     setup_complete, self._available)

                e = self.ensure_ssh()
                if not e and not setup_complete:
                    # This condition will update the libraries only once during
                    # application load time
                    e = self.ensure_lib()

                if e:
                    GObject.idle_add(self.emit, "error", e)
                else:
                    # Track challenge completed in kano-profile
                    tracker.track_action('make-light-setup-complete')
                    setup_complete = True
                    self._available = True

            elif not success:
                self._available = False

            GObject.idle_add(self.emit, "powerup-status", detected,
                             setup_complete, self._available)

            for dummy in xrange(20):
                if not self.thread_continue:
                    break
                time.sleep(0.25)

    def ensure_ssh(self):
        """
        Creates an ssh trust relationship between
        Powerup Kit Master and Slave units
        """

        # Generate a local ssh key file the first time
        if not os.path.exists(self.ssh_key_file):
            os.system('mkdir -p {}'.format(os.path.dirname(self.ssh_key_file)))
            err = os.system(
                'ssh-keygen -t rsa -f {} -N ""'.format(self.ssh_key_file)
            )
            if err != 0:
                # We are removing the keys so this operation is tried again
                try:
                    os.unlink(self.ssh_key_file)
                    os.unlink('{}.pub'.format(self.ssh_key_file))
                except Exception:
                    pass

                logger.error(
                    'Could not generate local SSH key for the Powerup Kit rc={}'
                    .format(err)
                )
                return 'Could not generate local SSH key'

        # Copy it across to the Power Kit always, to account for reflashed units
        err = os.system(
            'sshpass -p kano ssh {} {} mkdir -p .ssh'
            .format(self.ssh_options, self.ssh_address)
        )
        if err != 0:
            logger.error(
                'Could not create ssh directory on the remote Powerup Kit rc={}'
                .format(err)
            )
            return "Could not create remote .ssh directory"

        err = os.system(
            'sshpass -p kano scp {} {}.pub {}:.ssh/authorized_keys'
            .format(self.ssh_options, self.ssh_key_file, self.ssh_address)
        )
        if err != 0:
            logger.error(
                'Could not create ssh directory on the remot Powerup Kit rc={}'
                .format(err)
            )
            return "Could not copy SSH key to remote Powerup Kit"

        return None

    def ensure_lib(self, force_update=True):
        """
        Ensure the library is coped accross to the PI1.
        By default we always send it over for if the PI1 has been reflashed or
        completely replaced
        """

        req_libs = ['make_light', 'kano_peripherals']
        lib_base_path = '/usr/lib/python2.7/dist-packages'

        os.system('mkdir -p {}'.format(POWERUP_LOCAL_PATH))

        """
        Control if we already sent the libraries accross to the PI1
        This will eventually fail if the user swaps the PI1 to a new one,
        or reflashes the SD Card
        So by default we assume we have to send the libraries
        """
        if not force_update:
            if os.path.exists(self.lib_version_file):
                written_version = read_file_contents(self.lib_version_file)
                if written_version == lib_version:
                    return None

        err = os.system(
            'sshpass -p kano ssh {} {} mkdir -p  {}'
            .format(self.ssh_options, self.ssh_address, POWERUP_LOCAL_DIRNAME)
        )
        if err != 0:
            logger.error(
                'Could not create {} directory on the remote Powerup Kit rc={}'
                .format(POWERUP_LOCAL_DIRNAME, err)
            )
            return "Could not create remote powerup directory"

        for lib in req_libs:
            lib_path = os.path.join(lib_base_path, lib)
            err = os.system(
                'sshpass -p kano scp -r {} {} {}:{}'.format(
                    self.ssh_options,
                    lib_path,
                    self.ssh_address,
                    POWERUP_LOCAL_DIRNAME
                )
            )

            if err != 0:
                logger.error(
                    'Could not copy library "{}" to the remote Powerup Kit. '
                    'rc = {}'.format(lib, err)
                )
                return "Could not copy library to remote Powerup Kit"

        err = os.system(
            'sshpass -p kano scp -r {} {} {}:{}'.format(
                self.ssh_options,
                FONTS_DIR,
                self.ssh_address,
                POWERUP_LOCAL_DIRNAME
            )
        )

        if err != 0:
            logger.error(
                'Could not create ssh directory on the remote Powerup Kit rc={}'
                .format(err)
            )
            return "Could not copy library to remote Powerup Kit"

        write_file_contents(self.lib_version_file, lib_version)

        return None

    def _run_thr_target(self):
        """
        Transfers the code to the remote PI1 and executes
        it there, where the lighboard is attached
        """

        cmdline = 'scp -i {} {} {} {}:'.format(
            self.ssh_key_file, self.ssh_options, self.filename, self.ssh_address
        )
        e = os.system(cmdline)
        stderr = None
        if e:
            logger.error(
                'Error scp-ing code to the powerup kit: {}'
                .format(cmdline)
            )
            stderr = 'Error sending the code to the Powerup Kit'
        else:
            try:
                # Always kill old processes before running.
                cmdline = 'ssh -i {} {} {} "pkill -fx python.powerup-code-all.py; PYTHONPATH=~/.powerup/ python powerup-code-all.py"'.format(
                    self.ssh_key_file, self.ssh_options, self.ssh_address)
                e = subprocess.check_output(cmdline, shell=True,
                                            stderr=subprocess.STDOUT)
                print '#', e
            except subprocess.CalledProcessError as e:
                logger.error(
                    'Error executing code remotely: {}'
                    .format(cmdline)
                )
                stderr = e.output
                print '#', e.output

        self.running = False
        GObject.idle_add(self.emit, "finished-run", stderr)

    def shutdown(self):
        """
        Shut down the remote PI1. A lightboard code snippet is also run
        which turns the LEDs off before the kit goes to sleep.
        """

        try:
            # Construct a script to turn off the LEDs
            # by combining preamble and postamble
            wrap_code_path = '/usr/share/make-light/challenge_groups/'
            led_poweroff_script = 'led_poweroff.py'

            code_chunk = self.board.preamble
            code_chunk += '\n\nlight.all(False)\n\n'
            code_chunk += self.board.postamble

            led_poff_script_path = os.path.join('/tmp', led_poweroff_script)
            with open(led_poff_script_path, 'w') as f:
                f.writelines(code_chunk)

            chown_path(led_poff_script_path)

            # send the LED code to the remote PI1
            cmdline = 'scp -i {} {} {} {}:/tmp'.format(
                self.ssh_key_file,
                self.ssh_options,
                os.path.join('/tmp', led_poweroff_script),
                self.ssh_address
            )

            e = subprocess.check_output(
                cmdline, shell=True, stderr=subprocess.STDOUT
            )
        except Exception as e:
            logger.error(
                'Error preparing LEDs off code, exception {}, cmdline: {}'
                .format(e, cmdline)
            )

        # Even if we could not prepare the LED code,
        # send the remote poweroff anyways
        try:
            # Start the remote LED animation then power off the kit
            cmdline = 'ssh -i {} {} {} "PYTHONPATH=~/.powerup python /tmp/{} ; sudo poweroff"'.format(
                self.ssh_key_file, self.ssh_options, self.ssh_address, led_poweroff_script
            )

            e = subprocess.check_output(cmdline, shell=True, stderr=subprocess.STDOUT)
            print '#', e
        except subprocess.CalledProcessError as e:
            logger.error('Error executing code remotely: {}'.format(cmdline))
            stderr = e.output
            print '#', e.output

    def kill_code(self):
        """
        Stops the code running on the Powerup Kit
        """
        cmdline = 'ssh -i {} {} {} pkill -fx python.powerup-code-all.py'.format(
            self.ssh_key_file, self.ssh_options, self.ssh_address
        )
        rc = os.system(cmdline)
        if rc:
            logger.error('Error killing Powerup Kit code: rc={}'.format(rc))
            return False

        self.running = False

        return True
