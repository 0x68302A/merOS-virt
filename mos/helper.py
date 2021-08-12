#!/usr/bin/python3

import os
import os.path
import sys
import socket, struct
import getpass
import subprocess
import getopt
import datetime
from rich.console import Console
from rich.markdown import Markdown
import tarfile
import xml.etree.ElementTree as xml

class Helper:

	helper_path = os.path.dirname(os.path.realpath(__file__))
	mos_path = os.path.dirname(helper_path)

	uname = os.uname()
	arch = str(uname[4])

	euid = os.geteuid()
	uid = os.getuid()
	gid = os.getgid()

	host_ssh_pubkey_key_dir =  "/home/" + os.getlogin() + "/" + "./ssh/"
	mos_ssh_priv_key_dir = mos_path + "/data/ssh_keys"
	mos_img_dir = mos_path + "/data/images"

	
	# xml_conf_file = mos_path + "/conf" + "/" + target_distro + "/" + target_id + "/" + targetd_id + ".xml"


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
		
	def parse_xml(xml_conf_file):
		# Parse XML with ElementTree
		tree = ET.ElementTree(file=xml_conf_file)
		print(tree.getroot())
		root = tree.getroot()
		print("tag=%s, attrib=%s" % (root.tag, root.attrib))

		# get the information via the children!
		print("-" * 25)
		print("Iterating using getchildren()")
		print("-" * 25)
		users = root.getchildren()
		for user in users:
			user_children = user.getchildren()
			for user_child in user_children:
				print("%s=%s" % (user_child.tag, user_child.text))
		
		if __name__ == "__main__":
			parseXML("newdata.xml")
