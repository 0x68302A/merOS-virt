import src.config as config

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

class SSHCommunication:
    def __init__(self, target_full_id):
        self.target_full_id = target_full_id

        ## Import Gloval Variables
        h = config.Config()
        self.h = h
        self.mos_path  =  h.mos_path

        self.target_id_split = self.target_full_id.split("-")
        self.target_fam = self.target_id_split[0]
        self.target_id = self.target_id_split[1]

        self.target_id_xml = ( self.mos_path + "/conf/"
            + self.target_fam + "/build/"
            + self.target_id + ".xml" )

        self.mos_ssh_priv_key_dir = self.h.mos_ssh_priv_key_dir
        self.mos_ssh_key = self.mos_ssh_priv_key_dir + "/" + self.target_full_id + "-id_rsa"

        self.k = paramiko.RSAKey.from_private_key_file(self.mos_ssh_key)

        self.transport = paramiko.Transport((self.target_ip, int(self.target_ssh_port)))
        self.transport.connect(username = self.target_username, pkey = self.k )
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def interactive_shell_native(self):

        ssh_command = 'ssh -i ' + self.mos_ssh_key + ' ' + self.target_username + '@' + self.target_ip + ' -p ' + self.target_ssh_port
        subprocess.run(ssh_command, shell=True)

    def download_files(self, sftp_client, remote_dir, local_dir):

        if not self.exists_remote(sftp_client, remote_dir):
            return

        if not os.path.exists(local_dir):
            os.mkdir(local_dir)

        for filename in sftp_client.listdir(remote_dir):
            if stat.S_ISDIR(sftp_client.stat(remote_dir + filename).st_mode):
                # uses '/' path delimiter for remote server
                self.download_files(sftp_client, remote_dir
                                    + filename
                                    + '/', os.path.join(local_dir, filename))
            else:
                if not os.path.isfile(os.path.join(local_dir, filename)):
                    sftp_client.get(remote_dir + filename, os.path.join(local_dir, filename))


    def exists_remote(self, sftp_client, path):

        try:
            sftp_client.stat(path)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False
            raise
        else:
            return True


    def target_push(self, file):
        local_file = os.path.abspath(file)
        remote_path = "/home/user/mos-shared"
        remote_file  = os.path.join(remote_path, file)

        if os.path.isdir(local_file):
            sftp = SFTPClient_push.from_transport(self.transport)
            sftp.mkdir(remote_path, ignore_existing=True)
            sftp.put_dir(local_file, remote_path)
            sftp.close()


        elif os.path.isfile(local_file):
            self.sftp.put(local_file, remote_file)

        logging.info('Transfered "%s" to "%s"', file, self.target_full_id)

    def target_pull(self):

        local_path = os.path.join(self.mos_path, "data/mos-shared/", self.target_full_id)
        remote_path = "/home/user/mos-shared/"
        self.download_files(self.sftp, remote_path, local_path)

        logging.info('Pulled data from "%s"', self.target_full_id)

    def target_run(self, run_args):

        shell_waypipe_clean_local = ['rm', '-rf', '/tmp/socket_local']

        shell_waypipe_clean_remote = [
            'ssh',
            '-i', self.mos_ssh_key,
            f"{self.target_username}@{self.target_ip}",
            '-p', self.target_ssh_port,
            'rm -rf /tmp/socket_remote'
        ]

        shell_waypipe_listen = ['/usr/bin/waypipe', '-s', '/tmp/socket_local', 'client']

        shell_waypipe_bind = [
            'ssh',
            '-R', '/tmp/socket_remote:/tmp/socket_local',
            '-i', self.mos_ssh_key,
            f"{self.target_username}@{self.target_ip}",
            '-p', self.target_ssh_port,
            '/usr/bin/waypipe', '-s', '/tmp/socket_remote', 'server',
            '--',
            run_args
        ]

        process_cleanup_local = subprocess.Popen(shell_waypipe_clean_local, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_cleanup_remote = subprocess.Popen(shell_waypipe_clean_remote, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_waypipe_listen = subprocess.Popen(shell_waypipe_listen, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)
        process_waypipe_bind = subprocess.Popen(shell_waypipe_bind, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Started Local Waypipe with PID: {process_waypipe_listen.pid}")

        # Debug Waypipe
        ## with open('output.log', 'w') as outfile:
        ##     # Start the command and redirect stdout and stderr to the file
        ##     # process = subprocess.Popen(shell_waypipe_bind, stdout=outfile, stderr=subprocess.STDOUT)
        ##     process_waypipe_bind = subprocess.Popen(shell_waypipe_bind, stdout=outfile, stderr=subprocess.STDOUT)



        ##     # Optionally, wait for the process to complete
        ##     process_waypipe_bind.wait()

        ##     print("Process completed. Output written to output.log.")

class SFTPClient_push(paramiko.SFTPClient):
    def put_dir(self, source, target):
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        try:
            super(SFTPClient_push, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise
