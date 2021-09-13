import mos.helper as helper
import mos.target_get as target_get


import os
import socket
import sys
import paramiko
from paramiko.py3compat import u
import termios
import tty
import select

import struct
import fcntl
import signal
import errno

import logging

class SSHCommunication:
	def __init__(self, target_full_id):
		self.target_full_id = target_full_id

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
		self.mos_ssh_key = self.mos_ssh_priv_key_dir + "/" + self.target_full_id + "-id_rsa"

		self.xml_parse = helper.ParseXML(self.target_id_xml)
		self.target_ip = str(self.xml_parse.read_xml_value("network", "ip_addr"))
		self.target_ssh_port = str(self.xml_parse.read_xml_value("network", "ssh_port"))
		self.target_username = str(self.xml_parse.read_xml_value("details", "username"))

		self.k = paramiko.RSAKey.from_private_key_file(self.mos_ssh_key)
		self.sshClient = paramiko.SSHClient()
		self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.sshClient.connect( hostname = self.target_ip, username = self.target_username, port = self.target_ssh_port, pkey = self.k )

		self.channel = self.sshClient.get_transport().open_session()
		self.channel.get_pty(term="xterm")
		self.channel.invoke_shell()

	# thanks to Mike Looijmans for this code
	def interactive_shell(self):
		chan = self.channel
		oldtty = termios.tcgetattr(sys.stdin)
		try:
			tty.setraw(sys.stdin.fileno())
			tty.setcbreak(sys.stdin.fileno())
			chan.settimeout(0.0)
			signal.signal(signal.SIGWINCH, self.signal_winsize_handler)

			while True:
				try:
					r, w, e = select.select([chan, sys.stdin], [], [])
				except select.error as e:
					if e[0] != errno.EINTR: raise
				if chan in r:
					try:
						x = u(chan.recv(1024))
						if len(x) == 0:
							sys.stdout.write("\r\n*** EOF\r\n")
							break
						sys.stdout.write(x)
						sys.stdout.flush()
					except socket.timeout:
						pass
				if sys.stdin in r:
					x = sys.stdin.read(1)
					if len(x) == 0:
						break
					chan.send(x)

		finally:
			termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

		logging.info('connected to Target %s', self.target_full_id)

	def signal_winsize_handler(self, signum, frame):
		if signum == signal.SIGWINCH:
			s = struct.pack('HHHH', 0, 0, 0, 0)
			t = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
			winsize = struct.unpack('hhhh', t)
			self.channel.resize_pty(width=winsize[1], height=winsize[0])

	def target_push(self, file):
		local_file = os.path.abspath(file)

		transport = paramiko.Transport((self.target_ip, int(self.target_ssh_port)))
		transport.connect(username = self.target_username, pkey = self.k )

		sftp = paramiko.SFTPClient.from_transport(transport)

		# local_path = os.path.join(self.mos_path, "data/mos-shared/", self.target_full_id)
		# os.makedirs(local_path, mode = 0o777, exist_ok = True)
		remote_path = "/home/user/mos-shared"
		remote_file  = os.path.join(remote_path, file)

		if os.path.isdir(local_file):
			pass

		elif os.path.isfile(local_file):
			sftp.put(local_file, remote_file)


		'''
		TODO: MANAGE FOLDER TRANSFERS
		try:
			sftp.mkdir(path, mode)
		except IOError:
			pass

			for file in os.listdir(local_file):
				sftp.put(file, remote_file)
		'''
