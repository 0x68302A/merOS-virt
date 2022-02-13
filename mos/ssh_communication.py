import mos.helper as helper

import os
import socket
import sys
import subprocess
import paramiko
from paramiko.py3compat import u
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
		self.mos_ssh_key = self.mos_ssh_priv_key_dir + "/" + self.target_full_id + "-id_rsa"

		## Parse XML
		## Grabing Target- Specific SSH related Options
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

		self.transport = paramiko.Transport((self.target_ip, int(self.target_ssh_port)))
		self.transport.connect(username = self.target_username, pkey = self.k )
		self.sftp = paramiko.SFTPClient.from_transport(self.transport)


	## Grabed from Paramiko Examples
	## With an addition for Flexibe window size handling
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
			pass

		elif os.path.isfile(local_file):
			self.sftp.put(local_file, remote_file)

		logging.info('Transfered "%s" to "%s"', file, self.target_full_id)

	def target_pull(self):

		local_path = os.path.join(self.mos_path, "data/mos-shared/", self.target_full_id)
		remote_path = "/home/user/mos-shared/"
		self.download_files(self.sftp, remote_path, local_path)

		logging.info('Pulled data from "%s"', self.target_full_id)

	def target_run(self):

		self.xpra_args = ('xpra start --ssh'
				+ '="ssh -i '
				+ self.mos_ssh_key 
				+ ' -o "StrictHostKeyChecking=no""' ## data/ssh_keys/mos_mersec_deb-guest-id_rsa
				+ ' ssh://'
				+ self.target_username
				+ '@'
				+ self.target_ip + ':' + self.target_ssh_port
				+ ' --start=konsole')

		subprocess.Popen(self.xpra_args, shell=True)
