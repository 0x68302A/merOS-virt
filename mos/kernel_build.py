#!/usr/bin/python3

import mos
from mos import *

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
  kernel_build_dir = mos.mosPath + "/etc/build/kernel"
  kernel_git_dir = mos.mosPath + "/etc/build/kernel/linux"
  kernel_git_url = "https://github.com/torvalds/linux"

  os.chdir(kernel_build_dir)

  print("cloning into %s" % kernel_git_dir)
  git.Repo.clone_from(kernel_git_url, kernel_git_dir,
                      branch='master', progress=CloneProgress())

  #git.objects.submodule.base.UpdateProgress()
  #git.Git(kernel_build_dir).clone(kernel_git_url, depth=1)

  os.chdir(kernel_git_dir)

  subprocess.run(['make mrproper'], shell=True)
  subprocess.run(['make defconfig'], shell=True)

  with open('.config', 'a') as f:
   f.write('CONFIG_TUN=y')
   f.write('CONFIG_VIRTIO_PCI=y')
   f.write('CONFIG_VIRTIO_MMIO=y')

  subprocess.run(['make -j $(cat /proc/cpuinfo | grep processor | wc -l)'], shell=True)
  subprocess.run(['make headers_install'], shell=True)

  arch = x86 ## TODO Pass from helper
  bzimage_loc = mosPath + "arch" + arch + "/boot/bzImage"
  images_dir = mosPath + "/etc/images"
  shutil.copyfile(bzimage, images_dir)
