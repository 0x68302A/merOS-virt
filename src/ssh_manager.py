
import os
import socket
import sys
import subprocess
import paramiko
from paramiko.py3compat import u
import termios
import tty
import select
import time

import struct
import fcntl
import signal
import errno
import stat

import subprocess

import logging

from .app_config import AppConfig
from .vm_models import VMConfig, Config

class SSHManager:
    def __init__(self, config: Config, template: str, vm_name: str, vm_ip_addr: str, verbose: bool = False):
        self.config = config
        vm = self.config.virtual_machines[vm_name]
        self.mos_ssh_key = f"{AppConfig.mos_ssh_priv_key_dir}/{template}-{vm.name}-id_rsa"

        self.template = template
        self.vm_name = vm_name
        self.vm_username = vm.distribution
        self.vm_ip_addr = vm_ip_addr

    def interactive_shell(self):

            cmd = [
                "ssh",
                "-i", self.mos_ssh_key,
                f"{self.vm_username}@{self.vm_ip_addr}"
            ]

            subprocess.run(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

    def pull_files(self):

            cmd = [
                "rsync",
                "-av",
                f"-e ssh -i {self.mos_ssh_key}",
                f"{self.vm_username}@{self.vm_ip_addr}:/home/{self.vm_username}/mos-shared/",
                "--ignore-existing",
                "--progress",
                "--stats",
                "--human-readable",
                f"data/mos-shared/{self.template}-{self.vm_name}",
            ]

            subprocess.run(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

    def push_file(self, file_path: str):

            cmd = [
                "rsync",
                "-av",
                f"-e ssh -i {self.mos_ssh_key}",
                "--ignore-existing",
                "--progress",
                "--stats",
                "--human-readable",
                f"{file}",
                f"{self.vm_username}@{self.vm_ip_addr}:/home/{self.vm_username}/mos-shared/",
            ]

            subprocess.run(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    def vm_run(self, application: str):

        shell_waypipe_clean_local = ['rm', '-rf', '/tmp/socket_local']

        shell_waypipe_clean_remote = [
            'ssh',
            '-i', self.mos_ssh_key,
            f"{self.vm_username}@{self.vm_ip_addr}",
            'rm -rf /tmp/socket_remote'
        ]

        shell_waypipe_listen = ['/usr/bin/waypipe',
            '-s', '/tmp/socket_local',
            'client']

        shell_waypipe_bind = [
            'ssh',
            '-R', '/tmp/socket_remote:/tmp/socket_local',
            '-i', self.mos_ssh_key,
            f"{self.vm_username}@{self.vm_ip_addr}",
            '/usr/bin/waypipe', '-s', '/tmp/socket_remote', 'server',
            '--',
            application
        ]

        process_cleanup_lo = subprocess.Popen(shell_waypipe_clean_local, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_cleanup_vm = subprocess.Popen(shell_waypipe_clean_remote, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        process_listen = subprocess.Popen(shell_waypipe_listen, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)
        process_bind = subprocess.Popen(shell_waypipe_bind, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"Started Local Waypipe with PID: {process_listen.pid}")

        ## Debug Waypipe
        # with open('output.log', 'w') as outfile:
        #     # Start the command and redirect stdout and stderr to the file
        #     process = subprocess.Popen(shell_waypipe_bind, stdout=outfile, stderr=subprocess.STDOUT)
        #     process_waypipe_bind = subprocess.Popen(shell_waypipe_bind, stdout=outfile, stderr=subprocess.STDOUT)



        #     # Optionally, wait for the process to complete
        #     process_waypipe_bind.wait()

        #     print("Process completed. Output written to output.log.")
