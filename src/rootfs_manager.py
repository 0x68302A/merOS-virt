#!/usb/bin/python3

import os
import requests
import re
import sys
import string
import logging
import subprocess

from src.app_config import AppConfig

class RootfsManager:
    def __init__(self, distribution: str, arch: str):
        self.distribution = distribution
        self.arch = arch

        self.vm_bootstrap_dir = f"{AppConfig.mos_path}/data/build/bootstrap"
        self.distribution_rootfs_targz = f"{self.vm_bootstrap_dir}/rootfs_{self.distribution}_{self.arch}.tar.gz"
        self.distribution_rootfs_dir = f"{self.vm_bootstrap_dir}/rootfs_{self.distribution}_{self.arch}"


    def get_rootfs(self):
        if not os.path.isdir(self.vm_bootstrap_dir):
            os.makedirs(self.vm_bootstrap_dir)
        else:
            None

        os.chdir(self.vm_bootstrap_dir)

        if self.distribution == "alpine":
            logging.info('Downloading Alpine rootfs')
            self._get_alpine()
        elif self.distribution == "ubuntu":
            logging.info('Downloading Ubuntu rootfs')
            self._get_ubuntu()
        elif self.distribution == "debian":
            logging.info('Downloading Debian rootfs')
            self._get_debian()
        else:
            logging.info('Provided distribution is not supported')
            pass


        logging.info('Downloaded %s - %s rootfs', self.arch, self.distribution)

    def _get_alpine(self):

        alpine_mirror = "http://dl-cdn.alpinelinux.org/alpine/"
        alpine_mirror_releases_url = f"{alpine_mirror}latest-stable/releases/{self.arch}"
        alpine_mirror_release = f"{alpine_mirror}/latest-stable/releases/{self.arch}/latest-releases.yaml"
        alpine_latest_release = requests.get(alpine_mirror_release, allow_redirects=True)

        open("latest-releases.yaml", 'wb').write(alpine_latest_release.content)

        with open("latest-releases.yaml", "r") as file:
            for line in file:
                if re.search("file: alpine-minirootfs-.*.tar.gz", line):
                    vm_rootfs_id_full = str(line)
                    vm_rootfs_id_split = vm_rootfs_id_full.split()
                    vm_rootfs_id = vm_rootfs_id_split[1]

        vm_rootfs_url = alpine_mirror_releases_url + "/" + vm_rootfs_id
        vm_rootfs_url_request = requests.get(vm_rootfs_url, allow_redirects=True)
        open(self.distribution_rootfs_targz, 'wb').write(vm_rootfs_url_request.content)
        logging.info('Downloaded alpine Linux rootfs')

    def _get_ubuntu(self):

        vm_rootfs_url = ('https://cdimage.ubuntu.com/ubuntu-base/releases/'
                + 'focal/release/ubuntu-base-20.04.1-base-amd64.tar.gz')

        vm_rootfs_url_request = requests.get(vm_rootfs_url, allow_redirects=True)
        open(self.distribution_rootfs_targz, 'wb').write(vm_rootfs_url_request.content)
        logging.info('Downloaded alpine Ubuntu rootfs')

    def _get_debian(self):

        os.makedirs(self.distribution_rootfs_dir, mode = 0o777, exist_ok = True)
        self.debootstrap_args = ('debootstrap' ## We use debootstrap, as do most major other debian-based releases
                + ' --variant=minbase' ## Limiting final size is vital, we start with the "Required" Debian packages
                + ' stable ' ## Always build on stable release
                + self.distribution_rootfs_dir ## Build path
                + ' http://ftp.de.debian.org/debian' ) ##

        subprocess.run([self.debootstrap_args], shell=True)
