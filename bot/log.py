#!/usr/bin/env python

from collections import deque
import logging
import os
import time

class Handler(logging.FileHandler):
    def emit(self, record):
        super(Handler, self).emit(record)
        latest.appendleft((record.levelno, self.format(record)))

latest = deque(maxlen=50)

path = os.path.dirname(__file__) + '/logs/'
path = os.path.abspath(path + time.strftime('%y-%m-%d') + '.log')

formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s',
                              datefmt='%y-%m-%d at %I:%M:%S %p')

handler = Handler(filename=path, mode='a+')
handler.setFormatter(formatter)

logger = logging.getLogger('gobblerbot')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
