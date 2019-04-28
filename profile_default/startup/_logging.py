#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set up general logging parameters and write everything to separate files.

Logger
=======

Set up general logging. First situation where I'm creating logging and treating
it in a flexible, configurable way as if I was writing library code.

"""
import logging


def setup_ipython_logger():
    """Plug and play logging. No params so you can import and forget."""
    logger = logging.getLogger(name=__name__)
    logger.setLevel(logging.WARNING)

    # Set the filehandler to the name of the module importing this. Don't know
    # if that's how to do it correctly so cross your fingers!
    file_handler = logging.FileHandler(__name__ + '.log')
    formatter = logging.(
        '%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


logger = setup_ipython_logger()
