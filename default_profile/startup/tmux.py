#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tmux scripting. Inspired by xonsh's system calls."""
import gc
import subprocess


def tmux_new_window():
    return subprocess.run(
        ["tmux", "-u", "neww", "-Pdc", '"#{pane_current_path}"'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )

def garbage_collection():
    # random but last script
    ret = gc.collect()
    ret1 = gc.collect()
    counter = 2
    while ret != ret1:
        ret = gc.collect()
        counter += 1
    print(counter)

if __name__ == "__main__":
    garbage_collection()
