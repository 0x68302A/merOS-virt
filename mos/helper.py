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

class Helper:

	helper_path = os.path.dirname(os.path.realpath(__file__))
	mos_path = os.path.dirname(helper_path)

	uname = os.uname()
	arch = str(uname[4])

	euid = os.geteuid()
	uid = os.getuid()
	gid = os.getgid()

	mos_img_dir = mos_path + "/data/images/"
	mos_ssh_priv_key_dir = mos_path + "/data/ssh_keys"
	
	target_distro = "alpine"


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


class ParseXML:
	def __init__(self, xml_conf_file):
		self.xml_conf_file = xml_conf_file
		print(self.xml_conf_file)
		self.xml_data = open(self.xml_conf_file)
		self.xml_str = self.xml_data.read()
		self.xml_tree = ElementTree(fromstring(self.xml_str))
		self.xml_root = self.xml_tree.getroot()


	def read_xml(self, node, value):
		# print(self.xml_tree)
		for tag in self.xml_tree.findall(node):
			p_value = tag.get(value)
			return p_value


	def edit_xml(self, node, value, **kwargs):
		try:
			for element in self.xml_root.findall(node):
			        element.set(kwargs['attribute'],value)
			        element.set(attr,value)
			return ET.tostring(self.xml_root, encoding='unicode', method='xml')
		except NameError:
			pass

		for i in self.xml_root.iter(node):
			self.xml_root.set(node, value)
			i.text = value
		return ET.tostring(self.xml_root, encoding='unicode', method='xml')
