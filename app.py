#!/usr/bin/env python

from flask import Flask, g, jsonify, render_template, redirect, Response
from flask import request, url_for
from collections import deque
import bot
from bot.log import logger
from functools import wraps
import logging
import time
import sys
import config

__author__ = 'Alex Little'
__license__ = 'WTFPL'
__version__ = '0.0.1'

app = Flask(__name__)

def requires_auth(f):
    def validate(username, password):
        return username == config.username and password == config.password

    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization

        if not auth or not validate(auth.username, auth.password):
            return Response('', 401, {'WWW-Authenticate': 'Basic realm="%s"' %
                                      config.login_message})
        return f(*args, **kwargs)

    return wrapper

@app.before_request
def before():
    g.available = bot.tasks.available
    g.current = bot.tasks.current
    g.queue = list(enumerate(bot.tasks.queue.queue))

    g.len = len
    g.nav = []

    for name in ['about', 'status', 'tasks']:
        g.nav.append({ 'path': url_for(name), 'title': name.title() })

    g.nav = enumerate(g.nav)

    # The bot has stopped due to an error that occurred during task processing
    g.errored = bot.tasks.errored()

    # The bot was manually stopped
    g.stopped = bot.tasks.stopped() and bot.tasks.stop_sent()

    g.time = time
    g.version = __version__

@app.route('/')
def index():
    return redirect(url_for('about'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/status')
def status():
    status = 'good'
    msg = "I'm fine, captain."

    log = []
    warnings = 0

    for (level, record) in bot.log.latest:
        if level >= logging.WARNING:
            warnings += 1

        log.append(record)

    if bot.tasks.stop_sent():
        if not bot.tasks.stopped():
            status = 'warning'
            msg = 'Shutdown signal sent, waiting for bot to respond...'
        else:
            status = 'danger'
            msg = 'Manually stopped.'
    elif bot.tasks.errored():
        status = 'danger'
        msg = "Something's gone terribly wrong, captain!"
    elif warnings > 10:
        status = 'warning'
        msg = "I'm detecting elevated warning levels in the log, captain."

    return render_template('status.html', log=log, status=status, msg=msg)

@app.route('/start', methods=['POST'])
def start():
    msg = ''
    started = True

    try:
        bot.tasks.start()
    except Exception as e:
        msg = "Error: %s" % e.message
        started = False

    return jsonify(started=started, message=msg)

@app.route('/stop', methods=['POST'])
def stop():
    bot.tasks.stop()

    return jsonify(stop_sent=True)

@app.route('/shutdown', methods=['POST'])
@requires_auth
def shutdown():
    logger.critical('Emergency shutdown!')

    bot.tasks.stop()
    request.environ.get('werkzeug.server.shutdown')()

    return ''

@app.route('/tasks')
def tasks():
    return render_template('tasks.html')

@app.route('/tasks/add', methods=['POST'])
def tasks_add():
    msg = ''
    entry_id = False

    try:
        entry_id = bot.tasks.add(request.form['module'].strip(),
                request.form['name'].strip())
    except Exception as e:
        msg = "Error: %s" % e.message

    return jsonify(added=entry_id is not False, message=msg, entry_id=entry_id)

@app.route('/tasks/move', methods=['POST'])
def tasks_move():
    return jsonify(moved=bot.tasks.move(request.form['entry_id'],
                                        request.form['entry_position']))

@app.route('/tasks/remove', methods=['POST'])
def tasks_remove():
    return jsonify(removed=bot.tasks.remove(request.form['entry_id']))

if __name__ == '__main__':
    args = ['0.0.0.0', 80, False]

    if '--debug' in sys.argv:
        args = ['127.0.0.1', 5000, True]

    app.run(*args)


