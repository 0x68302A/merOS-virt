#!/usr/bin/python3

import mos.helper as helper

import os
import git
from git import Repo
from git import RemoteProgress
import subprocess

class CloneProgress(RemoteProgress):
	def update(self, op_code, cur_count, max_count=None, message=''):
		if message:
			print(message)

class KernelBuild():
	def kernel_make():
		
		h = helper.Helper()
		mos_path = h.mos_path
		mos_img_dir = h.mos_img_dir
		arch = h.arch
		
		kernel_git_url = "https://github.com/torvalds/linux"
		mos_kernel_build_dir = mos_path + "/data/build/kernel"
		mos_kernel_git_dir = mos_path + "/data/build/kernel/linux"
	
		os.chdir(mos_kernel_build_dir)
	
		print("cloning into %s" % mos_kernel_git_dir)
		git.Repo.clone_from(kernel_git_url, mos_kernel_git_dir,
				branch='master', progress=CloneProgress())
		os.chdir(mos_kernel_git_dir)
	
		subprocess.run(['make mrproper'], shell=True)
		subprocess.run(['make defconfig'], shell=True)
	
		with open('.config', 'a') as f:
			f.write('CONFIG_TUN=y')
			f.write('CONFIG_VIRTIO_PCI=y')
			f.write('CONFIG_VIRTIO_MMIO=y')
	
		subprocess.run(['make -j $(cat /proc/cpuinfo | grep processor | wc -l)'], shell=True)
		subprocess.run(['make headers_install'], shell=True)
	
		bzimage_loc = self.mos_path + "arch" + self.arch + "/boot/bzImage"
		shutil.copyfile(bzimage, self.mos_img_dir)
	
	'''
		TODO Add proggres tracker
		git.objects.submodule.base.UpdateProgress()
		git.Git(mos_kernel_build_dir).clone(kernel_git_url, depth=1)
	'''
