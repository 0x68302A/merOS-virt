#!/usr/bin/python3

import mos
from mos import *

import os
import os.path
import sys
import socket, struct
import getpass

import subprocess

import getopt
import datetime

helper_path = os.path.dirname(os.path.realpath(__file__))
mos_path = os.path.dirname(helper_path)

from rich.console import Console
from rich.markdown import Markdown

import tarfile

uname = os.uname()
arch = str(uname[4])

euid = os.geteuid()
uid = os.getuid()
gid = os.getgid()

host_ssh_pubkey_key_dir =  "/home/" + os.getlogin() + "/" + "./ssh/"

mos_ssh_priv_key_dir = mos_path + "/data/ssh-keys"
mos_img_dir = mos_path + "/data/images"

target_id = "mos-guest" # TODO Grab from ???
target_distro = "alpine" # TODO Grab from VM XML

def tProgress(): print(now.strftime('%H:%M:%S'))

def run_as_root(exec):
#	global euid
	if euid != 0:
		# print("merOS needs to run some commands as root, see more with -h")
		args = ['sudo', sys.executable] + sys.argv + [os.environ]
		# the next line replaces the currently-running process with the sudo
		os.execlpe('sudo', *args)

def drop_exec_priv():
	if euid == 0:
		os.seteuid(uid)

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

def tar_dir(output_filename, source_dir):
	with tarfile.open(output_filename, "w:") as tar:
		tar.add(source_dir, arcname=os.path.basename(source_dir))

def display_help():
    console = Console()
    with open("README.md", "r+") as help_file:
        console.print(Markdown(help_file.read()))
    sys.exit(0)
