#!/usr/bin/python3

import mos
from mos import *

import os
import os.path
import socket, struct
import getpass
import sys
import subprocess

import getopt
import datetime

from rich.console import Console
from rich.markdown import Markdown

import tarfile

mosPath = os.getcwd()
vmID = "mos-guest"
targetDistro = "alpine" # TODO Grab from VM XML

def tProgress():
  print(now.strftime('%H:%M:%S'))


euid = os.geteuid()
uid = os.getuid()
gid = os.getgid()

def runAsRoot(exec):
#	global euid
	if euid != 0:
		# print("merOS needs to run some commands as root, see more with -h")
		args = ['sudo', sys.executable] + sys.argv + [os.environ]
		# the next line replaces the currently-running process with the sudo
		os.execlpe('sudo', *args)

def drop_exec_priv():
	if euid == 0:
		os.seteuid(uid)

def getDefaultGatewayLinux():
	"""Read the default gateway directly from /proc."""
	with open("/proc/net/route") as fh:
		for line in fh:
			fields = line.strip().split()
			if fields[1] != '00000000' or not int(fields[3], 16) & 2:
		# If not default route or not RTF_GATEWAY, skip it
                		continue
			return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

defaultGw = str(getDefaultGatewayLinux())


def tarDir(output_filename, source_dir):
	with tarfile.open(output_filename, "w:") as tar:
		tar.add(source_dir, arcname=os.path.basename(source_dir))

def display_help():
    console = Console()
    with open("README.md", "r+") as help_file:
        console.print(Markdown(help_file.read()))
    sys.exit(0)
