import mos.helper as helper

import os
import subprocess
import socket
import sys
import termios
import tty
import select

import struct
import fcntl
import signal
import errno
import stat

import logging

class SSHCommunication:
	def __init__(self, target_full_id):
		self.target_full_id = target_full_id

		## Import Gloval Variables
		h = helper.Helper()
		self.h = h
		self.mos_path  =  h.mos_path

		self.target_id_split = self.target_full_id.split("-")
		self.target_fam = self.target_id_split[0]
		self.target_id = self.target_id_split[1]

		self.target_id_xml = ( self.mos_path + "/conf/target/"
				+ self.target_fam + "/build/"
				+ self.target_id + ".xml" )

		self.mos_ssh_priv_key_dir = self.h.mos_ssh_priv_key_dir
		self.target_ssh_key = self.mos_ssh_priv_key_dir + "/" + self.target_full_id + "-id_rsa"

		## Parse XML
		## Grabing Target- Specific SSH related Options
		self.xml_parse = helper.ParseXML(self.target_id_xml)
		self.target_ip = str(self.xml_parse.read_xml_value("network", "ip_addr"))
		self.target_ssh_port = str(self.xml_parse.read_xml_value("network", "ssh_port"))
		self.target_username = str(self.xml_parse.read_xml_value("details", "username"))

		logging.info('Connecting to %s@%s:%s - Using private key %s', self.target_username, self.target_ip, self.target_ssh_port, self.target_ssh_key)

	def interactive_shell(self):
		self.ssh_args = ('ssh -i '
					+ self.target_ssh_key
					+ ' '
					+ self.target_username + '@'
					+ self.target_ip
					+ ' -p ' + self.target_ssh_port
					+ ' -Y')

		subprocess.run([self.ssh_args], shell=True)


	def target_push(self, file):

		self.local_file = os.path.abspath(file)

		self.ssh_args = ('" ' + 'ssh'	+ ' -p ' + self.target_ssh_port
					+ ' -i ' + self.target_ssh_key + ' "')

		self.rsync_args = ('rsync -rzP --append -e '
					+ self.ssh_args
					+ ' ' + self.local_file
					+ ' ' + self.target_username + '@' + self.target_ip
					+ ':/home/user/mos-shared/')


		subprocess.run([self.rsync_args], shell=True)
		logging.info('Transfered "%s" to "%s"', file, self.target_full_id)


	def target_pull(self):


		self.ssh_args = ('" ' + 'ssh'	+ ' -p ' + self.target_ssh_port
					+ ' -i ' + self.target_ssh_key + ' "')

		self.rsync_args = ('rsync -rzP --append -e '
					+ self.ssh_args
					+ ' ' + self.target_username + '@' + self.target_ip
					+ ':/home/user/mos-shared/*'
					+ ' ' + os.path.join(self.mos_path, "data/mos-shared/", self.target_full_id))

		subprocess.run([self.rsync_args], shell=True)
