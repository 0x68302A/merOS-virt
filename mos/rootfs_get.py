#!/usb/bin/python3

import mos.helper as helper

import os
import requests
import re
import sys
import string
import logging

class RootfsGet:
	def __init__(self, target_distro):
		self.target_distro = target_distro

		## Import Global Variables
		h = helper.Helper()
		self.arch = h.arch

		self.target_bootstrap_dir = h.mos_path + "/data/build/bootstrap"
		self.distro_rootfs_targz = "rootfs" + "_" + self.target_distro + "_" + self.arch + ".tar.gz"

		## Define Release options
		## Such as URL and branch
		self.alpine_mirror = "http://dl-cdn.alpinelinux.org/alpine/"
		self.alpine_mirror_releases_url = self.alpine_mirror + "latest-stable/releases/" + self.arch
		self.alpine_mirror_release = self.alpine_mirror + "/latest-stable/releases/" + self.arch + "/latest-releases.yaml"


	def get_alpine(self):

		if not os.path.isdir(self.target_bootstrap_dir):
			os.makedirs(self.target_bootstrap_base_dir)
			os.makedirs(self.target_bootstrap_dir)
		else:
			None

		os.chdir(self.target_bootstrap_dir)

		alpine_latest_release = requests.get(self.alpine_mirror_release, allow_redirects=True)
		open("latest-releases.yaml", 'wb').write(alpine_latest_release.content)

		with open("latest-releases.yaml", "r") as file:
			for line in file:
				if re.search("file: alpine-minirootfs-.*.tar.gz", line):
					target_rootfs_id_full = str(line)
					target_rootfs_id_split = target_rootfs_id_full.split()
					target_rootfs_id = target_rootfs_id_split[1]

		target_rootfs_url = self.alpine_mirror_releases_url + "/" + target_rootfs_id
		target_rootfs_url_request = requests.get(target_rootfs_url, allow_redirects=True)
		open(self.distro_rootfs_targz, 'wb').write(target_rootfs_url_request.content)
		logging.info('Downloaded alpine Linux rootfs')


	## Create a handling Method
	## For Distro definition
	## TODO: Add a Debian Option
	def get_rootfs(self):
		tg = RootfsGet(self.target_distro)
		if self.target_distro == "alpine":
			logging.info('Downloading Alpine rootfs')
			tg.get_alpine()

		else:
			logging.info('Provided distribution is not supported')
			pass


		logging.info('Downloaded %s - %s rootfs from %s', self.arch, self.target_distro, self.alpine_mirror_releases_url)
