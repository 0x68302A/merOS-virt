#!/usr/bin/python3

import mos.helper as helper

import os
import git
from git import Repo
from git import RemoteProgress
import subprocess
import shutil
import logging

class CloneProgress(RemoteProgress):
	def update(self, op_code, cur_count, max_count=None, message=''):
		if message:
			print(message)

## We get the kernel from Git
## And build, using  custom configutarion
class KernelBuild:
	def __init__(self):

		## Universal Paths import
		## From Helper
		self.h = helper.Helper()
		self.mos_path = self.h.mos_path
		self.mos_img_dir = self.h.mos_img_dir
		self.arch = self.h.arch
		logging.info('System Architecture is %s', self.arch)

		## Kernel Git URL
		## And build path
		self.kernel_git_url = "https://github.com/torvalds/linux"
		self.mos_kernel_build_dir = self.mos_path + "/data/build/kernel"
		self.mos_kernel_git_dir = self.mos_path + "/data/build/kernel/linux"

		## Target bzimage path
		self.bzimage = self.mos_kernel_git_dir + "/arch/" + self.arch + "/boot/bzImage"


	## Kernel Cloning
	def kernel_clone(self):
		if os.path.exists(self.mos_kernel_git_dir):
			pass
		else:
			print("cloning into %s" % self.mos_kernel_git_dir)
			git.Repo.clone_from(self.kernel_git_url, self.mos_kernel_git_dir,
				depth=1, branch='master', progress=CloneProgress())


	## Kernel Building
	def kernel_build(self):

		## To manage build more efficiently
		## we chdir to build Path
		os.chdir(self.mos_kernel_git_dir)

		## Simple make preparation calls
		subprocess.run(['make mrproper'], shell=True)
		subprocess.run(['make defconfig'], shell=True)

		## Custom kernel Configuration options
		self.kernelopts = ("CONFIG TUN=y"
					+ "\nCONFIG_VIRTIO_PCI=y"
					+ "\nCONFIG_VIRTIO_MMIO=y")

		with open('.config', 'a') as f:
			f.write(self.kernelopts)

		## Final make calls
		subprocess.run(['make -j $(cat /proc/cpuinfo | grep processor | wc -l)'], shell=True)
		subprocess.run(['make headers_install'], shell=True)

		## Transfer bzimage from Build Path to Target Path - data/images/
		shutil.copyfile(self.bzimage, self.mos_img_dir + "bzImage")
