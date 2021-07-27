#!/usr/bin/python3

from mos import *
import subprocess
import apt
import shutil
import os

def host_tree_conf():
	os.makedirs(mos_path + "/data/build", mode = 0o777, exist_ok = True)
	os.makedirs(mos_path + "/data/build/kernel", mode = 0o777, exist_ok = True)
	os.makedirs(mos_path + "/data/build/bootstrap", mode = 0o777, exist_ok = True)
	os.makedirs(mos_path + "/data/images", mode = 0o777, exist_ok = True)
	os.makedirs(mos_path + "/data/ssh_keys", mode = 0o777, exist_ok = True)


def host_apt_conf():
	systemAdmin = ["iproute2", "nftables"]
	systemQemu = ["qemu-system", "libvirt-clients", "libvirt-daemon-system"]
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


def host_grub_conf():
	shutil.copyfile("conf/host/grub", "/etc/default/grub")
	subprocess.run(["update-grub"])
	print("grup-update was complete")


def host_syslink():
	sys_link = "/usr/bin/meros"

	os.remove(sys_link)
	os.symlink(mos_path + "/meros.py", sys_link)
