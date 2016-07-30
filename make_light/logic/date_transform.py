# date_transform.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Useful functions for transforimg date form JSON files

from datetime import datetime

DATE_ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def date_from_string(date_str):
    """ Generates a date object from an appropriately formated string
    :param date_str: Input date in string to be converted
    :type date_str: string like
    :returns: date object generated from the string
    :rtype: datetime.datetime
    :raises: ValueError if string is not in the right format
             TypeError if input is not string like
    """
    return datetime.strptime(date_str, DATE_ISO_FORMAT)
