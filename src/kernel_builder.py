#!/usr/bin/python3

import os
import shutil
import git
import subprocess
import logging

from git import Repo
from git import RemoteProgress

from src.app_config import AppConfig

class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            print(message)

## We get the kernel from Git
## And build, using  custom configutarion
class KernelBuilder:
    def __init__(self, verbose: bool = False):

        ## Universal Paths import
        ## From Config
        logging.info('System Architecture is %s', AppConfig.arch)

        ## Kernel Git URL
        ## And build path
        self.kernel_git_url = "https://github.com/torvalds/linux"
        self.mos_kernel_build_dir = AppConfig.mos_path + "/data/build/kernel"
        self.mos_kernel_git_dir = AppConfig.mos_path + "/data/build/kernel/linux"

        ## bzimage build path
        self.bzimage = self.mos_kernel_git_dir + "/arch/" + AppConfig.arch + "/boot/bzImage"
        ## bzimage Target path
        self.target_bzimage = AppConfig.mos_disk_dir + '/bzImage'

    ## Kernel Cloning
    def kernel_clone(self):

        if os.path.exists(self.mos_kernel_git_dir):
            pass
            logging.info('Kernel is already cloned')
        else:
            print("cloning into %s" % self.mos_kernel_git_dir)
            git.Repo.clone_from(self.kernel_git_url, self.mos_kernel_git_dir,
                depth=1, branch='master', progress=CloneProgress())


    ## Kernel Building
    def kernel_build(self):

        if os.path.isfile(self.target_bzimage):
            pass
            logging.info('Kernel is already built')
        else:

            ## To manage build more efficiently
            ## we chdir to build Path
            os.chdir(self.mos_kernel_git_dir)

            ## make prepare calls
            subprocess.run(['make clean'], shell=True)
            subprocess.run(['make mrproper'], shell=True)
            subprocess.run(['make defconfig'], shell=True)

            ## Custom kernel options for Virtualization support
            self.kernelopts = ("CONFIG_TUN=y"
                    + "\nCONFIG_VIRTIO_PCI=y"
                    + "\nCONFIG_VIRTIO_BLK=y"
                    + "\nCONFIG_OVERLAY_FS=y"
                    + "\nCONFIG_NET=y"
                    + "\nCONFIG_NETFILTER=y"
                    + "\nCONFIG_NETFILTER_ADVANCED=y"
                    + "\nCONFIG_NF_TABLES=y"
                    + "\nCONFIG_BRIDGE_NETFILTER=y"
                    + "\nCONFIG_BRIDGE=y"
                    + "\nCONFIG_NETFILTER_XT_MATCH_ADDRTYPE=y"
                    + "\nCONFIG_NETFILTER_XT_TARGET_MASQUERADE=y"
                    + "\nCONFIG_IP_NF_TARGET_MASQUERADE=y"
                    + "\nCONFIG_IP_NF_NAT=y"
                    + "\nCONFIG_VIRTIO_MMIO=y")

            with open('.mos_config', 'w') as f:
                f.write(self.kernelopts)

            subprocess.run(['./scripts/kconfig/merge_config.sh .config .mos_config'], shell=True)

            ## Final make calls
            subprocess.run(['make -j $(cat /proc/cpuinfo | grep processor | wc -l)'], shell=True)
            subprocess.run(['make headers_install'], shell=True)
            logging.info('Built Linux kernel from source')

            ## Transfer bzimage from Build Path to Target Path - data/images/
            shutil.copyfile(self.bzimage, self.target_bzimage)
