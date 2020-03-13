#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tmux scripting. Inspired by xonsh's system calls."""
import subprocess


def tmux_new_window():
    return subprocess.run(
        ["tmux", "-u", "neww", "-Pdc", '"#{pane_current_path}"'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
    )
