#!/usr/bin/env python

from collections import deque
import os
from log import logger
import shovel
import time
from uuid import uuid4
from threading import Event, Lock, Thread
from Queue import Empty, Queue

available = []
current = None
modules = []
queue = Queue(-1)

# The single worker thread
_worker = None

# Signal set by the current worker when an error occurs
_error = Event()

# Signal the current worker to stop
_stop = Event()

class Worker(Thread):
    daemon = True

    def run(self):
        while 1:
            if _error.is_set():
                break

            if _stop.is_set():
                logger.debug('Stop signal received by worker.')
                break

            try:
                entry = queue.get(False)
                task, id = (entry['task'], entry['id'])

                # Update current task
                current = entry

                logger.debug('Starting task %s.%s (%s)' % (entry['task'].module,
                                                           entry['task'].name,
                                                           entry['id'][:8]))
                entry['task']()

                logger.debug('Completed task (%s)' % entry['id'][:8])

            except Empty:
                break

            except Exception as e:
                _error.set()
                logger.exception(e)

            finally:
                current = None

def errored():
    return _error.is_set()

def start():
    """Start or restart task processing."""
    _error.clear()
    _stop.clear()

    logger.debug('Restarting worker.')

    if stopped():
        # Create new worker thread (they may only be used once).
        _worker = Worker()

    # Attempt to start the worker
    _worker.start()

def stop():
    """Send the stop signal to the current worker."""

    logger.debug('Manually stopping worker.')

    _stop.set()

def stop_sent():
    """Determine whether a stop signal has been sent to the current worker."""
    return _stop.is_set()

def stopped():
    """Determine whether the worker has actually stopped."""
    return _worker is None or not _worker.is_alive()

def add(module, name):
    """Add a task to the queue. Raises an exception if the task indicated does
    not exist, otherwise it returns the task's uuid."""

    for task in available:
        if task.module == module and task.name == name:
            id = uuid4().hex
            entry = {
                'added': time.time(),
                'id': id,
                'task': task
            }

            logger.debug('Added task %s.%s (%s)' % (task.module, task.name,
                                                    id[:8]))
            queue.put(entry)

            if not stop_sent():
                start()

            return id

    raise Exception('Unknown task.')

def move(id, position):
    position = int(position)
    moved = False

    if 0 <= position < len(queue.queue):
        new_queue = []

        for entry in queue.queue:
            if id == entry['id']:
                moved = entry
            else:
                new_queue.append(entry)

        if moved:
            new_queue.insert(position, moved)
            moved = True

        queue.queue = deque(new_queue)

    return moved

def remove(id):
    """Remove a task from the queue. Returns a boolean indicating whether the
    task was actually removed."""
    removed = False
    new_queue = []

    for entry in queue.queue:
        if id == entry['id']:
            logger.debug('Removed task %s' % id[:8])
            removed = True
        else:
            new_queue.append(entry)

    queue.queue = deque(new_queue)

    return removed

def _init():
    old_path = os.path.abspath('.')

    # Switch to this file's directory, temporarily, so that shovel sees shovel/
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    shovel.load()
    os.chdir(old_path)

    # List of tasks
    available.extend(shovel.Task.find())

    # List of task modules
    modules.extend(set([task.module for task in available]))

_init()

