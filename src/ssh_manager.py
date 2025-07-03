
import os
import sys
import subprocess
import logging
import time


from .app_config import AppConfig
from .vm_models import VMConfig, Config

class SSHManager:
    def __init__(self, config: Config, constellation: str, vm_name: str, vm_ip_addr: str, verbose: bool = False):
        self.config = config
        vm = self.config.virtual_machines[vm_name]
        self.mos_ssh_key = f"{AppConfig.mos_ssh_priv_key_dir}/{constellation}-{vm.name}-id_rsa"

        self.constellation = constellation
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
                f"{AppConfig.mos_path}/data/mos-shared/{self.constellation}-{self.vm_name}",
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
                f"{file_path}",
                f"{self.vm_username}@{self.vm_ip_addr}:/home/{self.vm_username}/mos-shared/",
            ]

            subprocess.run(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

    def vm_run(self, application: str):

        cmd_waypipe_clean_local = ['rm', '-rf', '/tmp/socket-local']

        cmd_waypipe_clean_remote = [
            'ssh', '-i', self.mos_ssh_key, f"{self.vm_username}@{self.vm_ip_addr}",
            'rm -rf /tmp/socket-remote'
        ]

        cmd_waypipe_listen_local = [
            '/usr/bin/waypipe',
            '--socket', '/tmp/socket-local', 'client'
        ]

        cmd_waypipe_bind_remote = [
            'ssh', '-i', self.mos_ssh_key, f"{self.vm_username}@{self.vm_ip_addr}",
            '-R', '/tmp/socket-remote:/tmp/socket-local',
            '/usr/bin/waypipe', '--socket', '/tmp/socket-remote', 'server',
            f"{application}"
        ]

        process_cleanup_local = subprocess.Popen(cmd_waypipe_clean_local, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_cleanup_remote = subprocess.Popen(cmd_waypipe_clean_remote, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        process_listen_local = subprocess.Popen(cmd_waypipe_listen_local, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)

        ## non-debug
        process_bind_remote = subprocess.Popen(cmd_waypipe_bind_remote, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"Started Local Waypipe with PID: {process_listen_local.pid}")

        ## debug
        # with open('output.log', 'w') as outfile:
        #     # Start the command and redirect stdout and stderr to the file
        #     process_waypipe_bind_remote = subprocess.Popen(cmd_waypipe_bind_remote, stdout=outfile, stderr=subprocess.STDOUT)

        #     # Optionally, wait for the process to complete
        #     process_waypipe_bind_remote.wait()

        #     print("Process completed. Output written to output.log.")
