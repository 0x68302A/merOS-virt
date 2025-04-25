#!/usr/bin/python3

import os
import os.path
import sys
import socket, struct
import getpass
import subprocess
import getopt
import datetime
import tarfile
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring, ElementTree
import random as r
import pydoc
import shutil

class AppConfig:
    ## Define MerOS path
    config_path = os.path.dirname(os.path.realpath(__file__))
    venv_path = sys.prefix if hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ) else None

    mos_path = os.path.dirname(venv_path)

    ## Define Host architecture
    uname = os.uname()
    arch = str(uname[4])

    euid = os.geteuid()
    uid = os.getuid()
    gid = os.getgid()

    ## Define some misc, basic Paths.
    mos_img_dir = mos_path + "/data/images"
    mos_ssh_priv_key_dir = mos_path + "/data/ssh_keys"

    target_distro = "alpine"

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

    ## We will be using that in our networked Targets
    ## As to resolve addresses seamlessely
    def get_default_gateway():
            """Read the default gateway directly from /proc."""
            with open("/proc/net/route") as fh:
                    for line in fh:
                            fields = line.strip().split()
                            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    # If not default route or not RTF_GATEWAY, skip it
                                                    continue
                            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

    default_gw = str(get_default_gateway())
