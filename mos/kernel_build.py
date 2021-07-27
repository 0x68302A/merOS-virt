#!/usr/bin/python3

import mos
from mos.helper import *

import os
import git
from git import Repo
from git import RemoteProgress
import subprocess

class CloneProgress(RemoteProgress):
	def update(self, op_code, cur_count, max_count=None, message=''):
		if message:
			print(message)

def kernel_build():
	kernel_build_dir = mos.mos_path + "/data/build/kernel"
	kernel_git_dir = mos.mos_path + "/data/build/kernel/linux"
	kernel_git_url = "https://github.com/torvalds/linux"

	os.chdir(kernel_build_dir)

	print("cloning into %s" % kernel_git_dir)
	git.Repo.clone_from(kernel_git_url, kernel_git_dir,
			    branch='master', progress=CloneProgress())
	os.chdir(kernel_git_dir)

	subprocess.run(['make mrproper'], shell=True)
	subprocess.run(['make defconfig'], shell=True)

	with open('.config', 'a') as f:
		f.write('CONFIG_TUN=y')
		f.write('CONFIG_VIRTIO_PCI=y')
		f.write('CONFIG_VIRTIO_MMIO=y')

	subprocess.run(['make -j $(cat /proc/cpuinfo | grep processor | wc -l)'], shell=True)
	subprocess.run(['make headers_install'], shell=True)

	bzimage_loc = mos_path + "arch" + arch + "/boot/bzImage"
	shutil.copyfile(bzimage, mos_img_dir)

'''
	TODO Add proggres tracker
	git.objects.submodule.base.UpdateProgress()
	git.Git(kernel_build_dir).clone(kernel_git_url, depth=1)
'''
