#!/usr/bin/python3

import mos.helper as helper

import subprocess
import apt
import shutil
import os

class HostConf:
	def __init__(self):
		h = helper.Helper()
		self.mos_path = h.mos_path
		print(self.mos_path)


	def tree_conf(self):
		os.makedirs(self.mos_path + "/data/build", mode = 0o777, exist_ok = True)
		os.makedirs(self.mos_path + "/data/build/kernel", mode = 0o777, exist_ok = True)
		os.makedirs(self.mos_path + "/data/build/bootstrap", mode = 0o777, exist_ok = True)
		os.makedirs(self.mos_path + "/data/images", mode = 0o777, exist_ok = True)
		os.makedirs(self.mos_path + "/data/ssh_keys", mode = 0o777, exist_ok = True)


	def apt_conf(self):
		systemAdmin = ["iproute2", "nftables"]
		systemQemu = ["qemu-system", "libvirt-clients", "libvirt-daemon-	system"]
		system_build = ["build-ninja", "libpixman-1-dev", "meson"]

		packageList = systemAdmin + systemQemu

		cache = apt.cache.Cache()
		cache.update()
		cache.open()

		for package in packageList:

			pkg_name = package
			pkg = cache[pkg_name]
			if pkg.is_installed:
				print("{pkg_name} already installed".format(pkg_name=pkg_name))
			else:
				pkg.mark_install()
				cache.commit()


	def grub_conf(self):
		shutil.copyfile("conf/host/grub", "/etc/default/grub")
		subprocess.run(["update-grub"])
		print("grup-update was complete")


	def syslink(self):
		sys_link = "/usr/bin/meros"
		
		if os.path.exists(sys_link):
			os.remove(sys_link)
		else:
			pass
		os.symlink(self.mos_path + "/meros.py", sys_link)

	def main(self):
		host_distro = "debian"
		hc = HostConf()

		hc.tree_conf()
		if host_distro == "ddebian":
			HostConf.apt_conf(self)
		else:
			pass

		hc.grub_conf()
		hc.syslink()
	