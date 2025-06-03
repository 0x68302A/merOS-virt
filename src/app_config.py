#!/usr/bin/python3

import os
import os.path
import sys
import socket, struct
import subprocess
import random as r
import pydoc

class AppConfig:
    ## Define meros path
    config_path = os.path.dirname(os.path.realpath(__file__))
    venv_path = sys.prefix if hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ) else None

    mos_path = os.path.dirname(venv_path)

    ## Define Host architecture
    uname = os.uname()
    arch = str(uname[4])

    ## Define some misc, basic Paths.
    mos_disk_dir = f"{mos_path}/data/disks"
    mos_ssh_priv_key_dir = f"{mos_path}/data/ssh_keys"
    mos_state_dir = f"{mos_path}/state"

    def display_help():
        with open(AppConfig.mos_path + "/src/manpage", "r") as help_file:
            help_data = help_file.read()
            pydoc.pager(help_data)

    def display_log():
        with open(AppConfig.mos_path + "/LOG", "r") as log_file:
            log_data = log_file.read()
            pydoc.pager(log_data)

    def elevate_privs():
        euid = os.geteuid()
        if euid != 0:
            # print("-- This action requires root access --\n-- Read more in the /meros comments --")
            args = ['sudo', sys.executable] + sys.argv + [os.environ]
            os.execlpe('sudo', *args)
