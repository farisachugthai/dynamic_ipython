#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import (
    jupyter_console_config,
    jupyter_contrib_nbextension_config,
    jupyter_labextension_config,
    jupyter_qtconsole_config,
    jupyter_serverextension_config,
)
from .jupyter_notebook_config import NonGraphicalEnvironmentError
from . import jupyter_notebook_config
import logging
import os
import sys

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
