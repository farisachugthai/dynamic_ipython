#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Move all randomly interspersed logging functions into one module."""
import datetime
import json
import logging
import os
import sys
import traceback


def _setup_logging(log_level=logging.WARNING,
                   time_format='%(asctime)s - %(name)s - %(message)s'):
    """Enable logging. TODO: Need to add more to the formatter."""
    logger = logging.getLogger(name=__name__)
    logger.setLevel(log_level)

    stream_handler_instance = logging.StreamHandler(sys.stdout)
    stream_handler_instance.setLevel(log_level)
    formatter = logging.Formatter(time_format)
    stream_handler_instance.setFormatter(formatter)
    logger.addHandler(stream_handler_instance)
    return logger


def path_logger():
    """Trying to put all of these functions in 1 spot."""
    logger = logging.getLogger(name=__name__)
    logger.setLevel(logging.WARNING)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def _logging(level, filename=None, shell=None, msg_format=None):
    """Shit we need to rewrite this function in it's entirety.

    To make it more extensible and widely used through the whole package,
    I attempted factoring out variables I usually hard code.

    Simple enough idea.

    But now there are SO many invariants because if the user doesn't set one,
    the following commands will fail.

    So we actually HAVE to specify a default value for everything.
    Which kinda decreases how modular this code is.

    However, if we don't then it literally won't work in the way it's written.
    Ergh this might get tough.

    Also should do some validation on the log level there. There's a really
    useful block of code in the tutorial.

    """
    logger = logging.getLogger(name=__name__)
    handler = logging.StreamHandler(sys.stdout)

    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.WARNING)

    if shell is not None:
        logdir = shell.profile_dir.log_dir
    # TODO: need an else fallback if shell is not none but filename is

    if filename is not None:
        log_file = os.path.join(logdir, 'keybinding.log')
        hdlr = logging.FileHandler(log_file)
        logger.addHandler(hdlr)
    # TODO: add stream handler in an else statement

    if msg_format is not None:
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)

    return logger


def json_logger():
    """Set up a logger that returns properly formatted JSON.

    Examples
    --------
    ::

        try:
            raise Exception('This is an exception')
        except:
            root_logger.exception('caught exception')

        root_logger.warn('this is a test message')
        root_logger.debug('this request_id=%d name=%s', 1, 'John')

    """
    handler = logging.StreamHandler()

    fmt = JsonFormatter()
    # add the formatter to the handler

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    return root_logger




class JsonFormatter(logging.Formatter):
    def format(self, record):
        if record.exc_info:
            exc = traceback.format_exception(*record.exc_info)
        else:
            exc = None

        return json.dumps({
            'msg': record.msg % record.args,
            'timestamp': datetime.datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'func': record.funcName,
            'level': record.levelname,
            'module': record.module,
            'process_id': record.process,
            'thread_id': record.thread,
            'exception': exc
        })
