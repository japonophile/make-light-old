#!/usr/bin/env python
# This file needs to be prepended to tutorial files, for
# them to work

import os
import sys

from kano.utils import get_user_unsudoed, get_home_by_username
DIR_PATH = os.path.join(
    get_home_by_username(get_user_unsudoed()), 'make-light'
)

if __name__ == '__main__' and __package__ is None:
    if DIR_PATH != '/usr':
        sys.path.insert(1, DIR_PATH)

from make_light.boards.base.aliases import *
from time import *
import time
from datetime import datetime
import datetime
from random import *
import random
from math import *
import math
