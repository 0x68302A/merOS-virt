#!/usb/bin/python3

import mos
from mos.helper import *

import os
import requests
import re
import sys
import string
import tarfile

target_bootstrap_dir = mos.mos_path + "/data/build/bootstrap/" + mos.target_distro
target_bootstrap_base_dir = mos.mos_path + target_bootstrap_dir + "/base"

alpine_mirror = "http://dl-cdn.alpinelinux.org/alpine/"
alpine_mirror_releases_url = alpine_mirror + "latest-stable/releases/" + arch + "/"
alpine_mirror_release = alpine_mirror + "latest-stable/releases/" + arch + "/latest-releases.yaml"

rootfs_targz = "rootfs" + target_distro + arch

def target_bootstrap():

	DNS1 = "1.1.1.1"
	DNS2 = "1.0.0.1"

	if not os.path.isdir(target_bootstrap_dir):
		os.makedirs(target_bootstrap_base_dir)
		os.makedirs(target_bootstrap_dir)
	else:
		None

	os.chdir(target_bootstrap_dir)

	latest_release = requests.get(alpine_mirror_release, allow_redirects=True)
	open("latest-releases.yaml", 'wb').write(alpine_latest_release.content)

	with open("latest-releases.yaml", "r") as file:
		for line in file:
			if re.search("file: alpine-minirootfs-.*.tar.gz", line):
				target_rootfs_id_full = str(line)
				target_rootfs_id_split = rootfs_id_full.split()
				target_rootfs_id = rootfs_id_split[1]

	target_rootfs_url = alpine_mirror_releases_dir + rootfs_id
	rootfs_file = requests.get(target_rootfs_ink, allow_redirects=True)
	open(rootfs_targz, 'wb').write(target_rootfs.content)
