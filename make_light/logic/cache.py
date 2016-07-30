# cache.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


import os
import json
import shutil
import re

from kano.logging import logger
from kano.utils import chown_path

from make_light.errors import SAVE_EXISTS_ERROR, RENAME_LIMIT_ERROR, \
    UNEXPECTED_ERROR
from make_light.paths import SAVE_DIR, GIF_DIR, GIF_FILE_NAME, \
    CODE_FILE_EXTENSION, SHARE_INFO_FILE_EXTENSION, ANIMATION_FILE_EXTENSION


class CodeCache(object):
    """
    """

    MAX_RENAME_INDEX = 100  # for duplicate filenames

    _singleton_instance = None

    @staticmethod
    def get():
        if not CodeCache._singleton_instance:
            CodeCache()
        return CodeCache._singleton_instance

    def __init__(self):
        if CodeCache._singleton_instance:
            raise Exception('This class is a singleton!')
        else:
            CodeCache._singleton_instance = self

        self.code_cache = dict()
        self.last_saved_code_path = ''
        self.last_saved_info = dict()

        self._load_saves()
        self.code_cache[''] = True  # ignore empty saves

    def _load_saves(self):
        code_file_paths = list()

        # go through the Local folder and get the full paths
        # to the .lightcode files
        for save_file in os.listdir(SAVE_DIR):
            if save_file.endswith(CODE_FILE_EXTENSION):
                code_file_paths.append(os.path.join(SAVE_DIR, save_file))

        # read each lightcode file and hash its contents
        for code_file_path in code_file_paths:
            try:
                with open(code_file_path, 'r') as f:
                    code = f.read()

                code = self._standardise(code)
                self.code_cache[code] = True

            except (IOError, OSError) as e:
                logger.warn('Could not read the lightcode files for CodeCache'
                            ' - [{}]'.format(e))
            except Exception as e:
                logger.warn('Unexpected error while reading the lightcode files'
                            ' - [{}]'.format(e))

    def save(self, code, data, rename=True):
        """
        Save the code, metadata, and animation.

        Args:
            code: A string containing the lightcode.
            data: A dict containing 'title' and 'description' about the save.
            rename: Will attempt to save by renaming with an index.

        Returns:
            A dict containing a Standard Error if it occurred
            or NoneType otherwise.
        """
        if self._standardise(code) is '':
            return  # ignore empty code

        rv = self._generate_files(data, rename)
        if isinstance(rv, dict):
            return rv  # there was an error

        try:
            code_file, info_file, anim_file = rv
            board_name = data['hwRef']['code']

            decorated_code = self._add_board_magic_metadata(code, board_name)

            # save the code
            with open(code_file, 'w') as f:
                f.write(decorated_code)
            chown_path(code_file)

            # save the metadata about the save
            with open(info_file, 'w') as f:
                json.dump(data, f, indent=4)
            chown_path(info_file)

            # copy the gif from the tmp to the local dir
            shutil.copyfile(os.path.join(GIF_DIR, GIF_FILE_NAME), anim_file)

            # finally, cache the saved code
            code = self._standardise(code)
            self.code_cache[code] = True
            self.last_saved_code_path = code_file
            self.last_saved_info = data

        except (IOError, OSError) as e:
            logger.error('Could not create necessary files for saving'
                         ' - [{}]'.format(e))
            return UNEXPECTED_ERROR

        except Exception as e:
            logger.warn('Unexpected error while saving the lightcode'
                        ' - [{}]'.format(e))
            return UNEXPECTED_ERROR

    @staticmethod
    def _add_board_magic_metadata(code, board_name):
        """ Add the magic number and metadata on the top of the file that is
        about to be written to disk. This is necessary so that make-light
        knows what kind of HW is required to load a share
        :param code: The code to be decorated with the magic no and metadata
        :type code: basestring
        :param board_name: Name of the HW board that this code is associated
                           with.
        :type board_name: basestring
        """
        tagged_code = '# KANOLIGHT {}\n'.format(
            json.dumps({'board_type': board_name})
        )
        tagged_code += code
        return tagged_code

    @staticmethod
    def _extract_magic_metadata(code):
        """ Exctract the metadata that decorate the code. Return code as it is
        if no metadata are found
        """
        default_board = 'Lightboard'
        top = re.compile(
            r'^# KANOLIGHT (\{.*?\})$\n(.*)',
            flags=(re.MULTILINE | re.DOTALL)
        )
        matches = top.match(code)

        board_name = default_board
        cleaned_code = code
        if matches:
            metadata_raw = matches.group(1)
            cleaned_code = matches.group(2)
            try:
                meta = json.loads(metadata_raw)
                board_name = meta['board_type']
            except (TypeError, ValueError, KeyError) as exc_err:
                logger.warn(
                    'Metadata dict not in the right format [{}]'
                    .format(exc_err)
                )

        return (cleaned_code, board_name)

    def is_saved(self, code):
        """
        Check if the given code has been previously saved.

        Args:
            code: A string containing the lightcode.

        Returns:
            True if the given code was saved, false otherwise.
        """
        code = self._standardise(code)
        return code in self.code_cache

    def load(self, code_path):
        """
        Get the lightcode from the given file path.

        Args:
            code_path: A path to a lightcode file.

        Returns:
            A string with the lightcode read from the given path.
            If an error occurred, returns an empty string.
        """
        code = ''

        # verifying the path we received
        if not os.path.isfile(code_path) and \
           not code_path.endswith(CODE_FILE_EXTENSION):
            logger.warn('Attempted to load path but file does not exist')

        try:
            # read the code from the file
            with open(code_path) as f:
                code = f.read()

        except (IOError, OSError) as e:
            logger.error('Could not load file {} - [{}]'.format(code_path, e))

        except Exception as e:
            logger.warn('Unexpected error while loading the lightcode'
                        ' - [{}]'.format(e))

        code, board_type = self._extract_magic_metadata(code)

        return (code, board_type)

    def get_last_saved_code_file(self):
        """
        Get the filepath for the last saved code.

        Returns:
            Filepath to the last saved .lightcode file or empty string
            if nothing was saved yet.
        """
        return self.last_saved_code_path

    def get_last_saved_info(self):
        """
        Get the title and description of the last save.

        Returns:
            Dict with 'title' and 'description' fields or empty dict
            if nothing was saved yet.
        """
        return self.last_saved_info

    def _standardise(self, code):
        try:
            return code.strip().upper()

        except Exception as e:
            logger.warn('Unexpected error while standardising the lightcode'
                        ' - [{}]'.format(e))
            return ''

    def _generate_files(self, data, rename):
        title = data['title']
        # description = data['description']

        index = 0
        while index < self.MAX_RENAME_INDEX:
            if index == 0:
                file_template = os.path.join(
                    SAVE_DIR, '{title}.{{extension}}'.format(title=title)
                )
            else:
                file_template = os.path.join(
                    SAVE_DIR, '{title} ({index}).{{extension}}'
                              .format(title=title, index=index)
                )
            code_file = file_template.format(extension=CODE_FILE_EXTENSION)
            info_file = file_template.format(extension=SHARE_INFO_FILE_EXTENSION)
            anim_file = file_template.format(extension=ANIMATION_FILE_EXTENSION)

            # if none of the files exist, only then proceed
            if not os.path.exists(code_file) and \
               not os.path.exists(info_file) and \
               not os.path.exists(anim_file):
                return (code_file, info_file, anim_file)

            # if we need to rename, try adding an index
            elif rename is False:
                return SAVE_EXISTS_ERROR

            # increase the rename index
            index += 1

        # too many saves with the same title and renamed
        return RENAME_LIMIT_ERROR
