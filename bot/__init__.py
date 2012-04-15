#!/usr/bin/env python

import os
import sys

# This is needed so that the tasks in shovel/ can see the rest of the bot. I'd
# use relative imports but shovel doesn't recognize tasks in packages, for
# whatever reason.
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import db
import log
import tasks
