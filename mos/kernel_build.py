#!/usr/bin/python3

import mos.helper as helper

import os
import git
from git import Repo
from git import RemoteProgress
import subprocess
import shutil

class CloneProgress(RemoteProgress):
	def update(self, op_code, cur_count, max_count=None, message=''):
		if message:
			print(message)

class KernelBuild:
	def __init__(self):
		self.h = helper.Helper()
		self.mos_path = self.h.mos_path
		self.mos_img_dir = self.h.mos_img_dir
		self.arch = self.h.arch
		print(self.arch)
		
		self.kernel_git_url = "https://github.com/torvalds/linux"
		self.mos_kernel_build_dir = self.mos_path + "/data/build/kernel"
		self.mos_kernel_git_dir = self.mos_path + "/data/build/kernel/linux"
		
		self.bzimage = self.mos_kernel_git_dir + "/arch/" + self.arch + "/boot/bzImage"


	def kernel_clone(self):
		if os.path.exists(self.mos_kernel_git_dir):
			pass
		else:
			print("cloning into %s" % self.mos_kernel_git_dir)
			git.Repo.clone_from(self.kernel_git_url, self.mos_kernel_git_dir,
				depth=1, branch='master', progress=CloneProgress())


	def kernel_build(self):
		
		if os.path.exists(self.bzimage):
			pass
		else:
			os.chdir(self.mos_kernel_git_dir)
			
			subprocess.run(['make mrproper'], shell=True)
			subprocess.run(['make defconfig'], shell=True)
			
			with open('.config', 'a') as f:
				f.write('CONFIG_TUN=y')
				f.write('CONFIG_VIRTIO_PCI=y')
				f.write('CONFIG_VIRTIO_MMIO=y')
				
			subprocess.run(['make -j $(cat /proc/cpuinfo | grep processor | wc -l)'], shell=True)
			subprocess.run(['make headers_install'], shell=True)
			
		shutil.copyfile(self.bzimage, self.mos_img_dir + "bzImage")
