#!/usb/bin/python3

import src.config as config

import os
import requests
import re
import sys
import string
import logging
import subprocess

class RootfsGet:
	def __init__(self, target_distro):
		self.target_distro = target_distro

		## Import Global Variables
		h = config.Config()
		self.arch = h.arch

		self.target_bootstrap_dir = h.mos_path + "/data/build/bootstrap"
		self.distro_rootfs_targz = "rootfs" + "_" + self.target_distro + "_" + self.arch + ".tar.gz"
		self.distro_rootfs_dir = "rootfs" + "_" + self.target_distro + "_" + self.arch

		## Define Release options
		## Such as URL and branch
		self.alpine_mirror = "http://dl-cdn.alpinelinux.org/alpine/"
		self.alpine_mirror_releases_url = self.alpine_mirror + "latest-stable/releases/" + self.arch
		self.alpine_mirror_release = self.alpine_mirror + "/latest-stable/releases/" + self.arch + "/latest-releases.yaml"


	def get_alpine(self):

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

	def get_ubuntu(self):

		target_rootfs_url = ('https://cdimage.ubuntu.com/ubuntu-base/releases/'
				+ 'focal/release/ubuntu-base-20.04.1-base-amd64.tar.gz')

		target_rootfs_url_request = requests.get(target_rootfs_url, allow_redirects=True)
		open(self.distro_rootfs_targz, 'wb').write(target_rootfs_url_request.content)
		logging.info('Downloaded alpine Ubuntu rootfs')

	def get_debian(self):

		os.makedirs(self.distro_rootfs_dir, mode = 0o777, exist_ok = True)
		self.debootstrap_args = ('debootstrap' ## We use debootstrap, as do most major other debian-based releases
				+ ' --variant=minbase' ## Limiting final size is vital, we start with the "Required" Debian packages
				+ ' stable ' ## Always build on stable release
				+ self.distro_rootfs_dir ## Build path
				+ ' http://ftp.de.debian.org/debian' ) ## 

		subprocess.run([self.debootstrap_args], shell=True)



	## Create a handling Method
	## For Distro definition
	## TODO: Add a Debian Option
	def get_rootfs(self):
		if not os.path.isdir(self.target_bootstrap_dir):
			os.makedirs(self.target_bootstrap_base_dir)
			os.makedirs(self.target_bootstrap_dir)
		else:
			None

		os.chdir(self.target_bootstrap_dir)

		tg = RootfsGet(self.target_distro)
		if self.target_distro == "alpine":
			logging.info('Downloading Alpine rootfs')
			tg.get_alpine()
		elif self.target_distro == "ubuntu":
			logging.info('Downloading Ubuntu rootfs')
			tg.get_ubuntu()
		elif self.target_distro == "debian":
			logging.info('Downloading Debian rootfs')
			tg.get_debian()


		else:
			logging.info('Provided distribution is not supported')
			pass


		logging.info('Downloaded %s - %s rootfs', self.arch, self.target_distro)
