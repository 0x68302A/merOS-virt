#!/usr/bin/python3

from mos import *
import subprocess
import apt
import shutil
import os

def sys_apt_conf():
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

def sys_tree_conf():
	os.makedirs(mos_path + "/etc/build", mode = 0o777, *, exist_ok = False)
	os.makedirs(mos_path + "/etc/images", mode = 0o777, *, exist_ok = False)
	os.makedirs(mos_path + "/etc/ssh_keys", mode = 0o777, *, exist_ok = False)


def sys_grub_conf():
  shutil.copyfile("etc/host/grub", "/etc/default/grub")
  subprocess.run(["update-grub"])
  print(mosPath)
  print("grup-update was complete")

sys_link = "/usr/bin/meros"

def sys_link_set():
	os.remove(sys_link)
	os.symlink(mosPath + "/meros.py", sys_link)
