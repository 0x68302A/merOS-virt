#!/usr/bin/python3

import mos.helper as helper

import subprocess
import apt
import shutil
import os
import logging

class HostConf:
	def __init__(self):
		h = helper.Helper()
		self.mos_path = h.mos_path

	def tree_conf(self):
		os.makedirs(self.mos_path + "/data/build", mode = 0o777, exist_ok = True)
		os.makedirs(self.mos_path + "/data/build/kernel", mode = 0o777, exist_ok = True)
		os.makedirs(self.mos_path + "/data/build/bootstrap", mode = 0o777, exist_ok = True)
		os.makedirs(self.mos_path + "/data/images", mode = 0o777, exist_ok = True)
		os.makedirs(self.mos_path + "/data/ssh_keys", mode = 0o777, exist_ok = True)
		os.makedirs(self.mos_path + "/data/proc", mode = 0o777, exist_ok = True)
		os.makedirs(self.mos_path + "/data/mos-shared", mode = 0o777, exist_ok = True)
		os.makedirs(self.mos_path + "/conf/target", mode = 0o777, exist_ok = True)
		logging.info('Created Directory Tree, all data created by us are now found under ./data')

	def syslink(self):
		sys_link = "/usr/bin/meros"

		if os.path.islink(sys_link):
			os.remove(sys_link)
		else:
			pass


		os.symlink(self.mos_path + "/meros.py", sys_link)
		logging.info('Created symlink of meros.py. /nMerOS can now be run ( as root ) simply by calling meros')

	def main(self):
		host_distro = "debian"
		hc = HostConf()

		hc.tree_conf()
		if host_distro == "ddebian":
			HostConf.apt_conf(self)
		else:
			pass

		hc.syslink()
