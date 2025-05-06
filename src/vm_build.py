#!/usr/bin/python3

import os
import distutils, distutils.dir_util
import tarfile
import subprocess
import glob
import time
import logging
import guestfs
from typing import Dict, Optional, Tuple

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

from src.vm_models import VMConfig, Config, VirtualDisk
from src.app_config import AppConfig
from src.rootfs_manager import RootfsManager

logger = logging.getLogger(__name__)

class VMBuilder:
    def __init__(self, config: Config, template: str, verbose: bool = False):
        self.config = config
        self.template = template

        if verbose:
            logger.setLevel(logging.DEBUG)

    def build_vm(self, vm_name: str):
        vm = self.config.virtual_machines[vm_name]
        logger.info(f"Building VM: {vm_name}")
        start_time = time.time()
        app_config = AppConfig()

        self.running_uid = int(os.getenv('SUDO_UID'))
        self.running_gid = int(os.getenv('SUDO_GID'))

        ## Template ( source ) files
        self.source_conf_dir = f"{AppConfig.mos_path}/templates/{self.template}"
        self.source_conf_rootfs_dir = f"{self.source_conf_dir}/rootfs/{vm_name}/includes.chroot"
        self.source_conf_rootfs_common_dir = f"{self.source_conf_dir}/rootfs/common/includes.chroot"
        self.source_hooks_dir = f"{self.source_conf_dir}/rootfs/{vm_name}/hooks"
        self.source_pkgs_dir = f"{self.source_conf_dir}/pkg/"

        ## Chroot ( final ) files
        self.chroot_dir = f"{AppConfig.mos_path}/data/build/bootstrap/{self.template}/{vm_name}/"
        self.chroot_hooks_dir = f"{self.chroot_dir}/tmp/src/hooks"
        self.chroot_pkgs_dir = f"{self.chroot_dir}/opt"
        self.chroot_ssh_dir = f"{self.chroot_dir}/etc/ssh"

        ## Build ( host ) files
        self.rootfs_tar = f"{AppConfig.mos_path}/data/build/bootstrap/{self.template}/{vm_name}.tar"
        self.rootfs_img = f"{AppConfig.mos_disk_dir}/{self.template}-{vm_name}.qcow2"

        try:
            # Prepare rootfs
            self._rootfs_manage(vm_name, vm.distribution, vm.arch)
            self._chroot_configure(vm_name)
            self._chroot_keyadd(vm_name)
            logger.debug(f"Building tar for: {vm_name}")
            self._rootfs_tar_build(vm_name)
            logger.debug(f"Building qcow2 for: {vm_name}")
            self._rootfs_qcow_build(vm_name)

        except Exception as e:
            logger.error(f"Failed to build VM: {e}")
            raise

    ## Get, Unpack, and Place rootfs
    def _rootfs_manage(self, vm_name: str, vm_distribution : str, vm_arch: str):

        ## Check for VM chroot /sbin/init, and skip rootfs download if found.
        ## TODO: add an update flag to --build,
        ## as to allow for updating the base rootfs
        self.vm_name = vm_name
        self.vm_distribution = vm_distribution
        self.vm_arch = vm_arch
        self.rootfs_manager = RootfsManager(vm_distribution, vm_arch)
        if os.path.exists(self.chroot_dir + "/usr/bin/"):
            None
            logging.info('Chroot is already populated with /usr/bin/ - Skipping rootfs download')
        else:

            logging.info('Processing rootfs requirments')

            self.rootfs_manager.get_rootfs()
            os.makedirs(self.chroot_dir, mode = 0o777, exist_ok = True)

            ## Check whether we're dealing with a tar.gzip ROOTFS
            if os.path.isfile(self.rootfs_manager.distribution_rootfs_targz):
                tar_file = tarfile.open(self.rootfs_manager.distribution_rootfs_targz)
                tar_file.extractall(self.chroot_dir)
                tar_file.close

            ## Or a common path
            elif os.path.exists(self.rootfs_manager.distribution_rootfs_dir):
                self.cp_args = ('cp -rn '
                    + self.rootfs_manager.distribution_rootfs_dir
                    + '/* ' + self.chroot_dir)
                subprocess.run(self.cp_args, shell=True)
            else:
                logging.info('Can not find distribution ROOTFS')


    ## Configure the above rootfs
    ## In a Chroot enviroment
    def _chroot_configure(self, vm_name: str):

        try:
            distutils.dir_util.copy_tree(self.source_conf_rootfs_common_dir, self.chroot_dir)
        except:
            logging.info('No common rootfs Configuration found')

        distutils.dir_util.copy_tree(self.source_conf_rootfs_dir, self.chroot_dir)
        distutils.dir_util.copy_tree(self.source_hooks_dir, self.chroot_hooks_dir)
        distutils.dir_util.copy_tree(self.source_pkgs_dir, self.chroot_pkgs_dir)

        ## Chroot to VM
        f = os.open("/", os.O_PATH)
        os.chdir(self.chroot_dir)

        os.chroot(".")

        ## TODO: Fix DNS resolution for building
        with open("/etc/resolv.conf", 'w') as file:
                file.write("nameserver 1.1.1.1")

        subprocess.run("/tmp/src/hooks/0100-conf.chroot", shell=True)
        subprocess.run("/tmp/src/hooks/0150-packages.chroot", shell=True)
        os.chdir(f)
        os.chroot(".")

    def _chroot_keyadd(self, vm_name: str):
        self.vm_name = vm_name

        ## Used for VM ssh_host_rsa_key
        self.host_key = SSHKeys()
        ssh_private_key_01 = self.host_key.private_key

        with open(self.chroot_ssh_dir + "/ssh_host_rsa_key", 'w') as content_file:
            content_file.write(ssh_private_key_01)

        os.chmod(self.chroot_ssh_dir + "/ssh_host_rsa_key", 0o0600)

        ## Used for Key_based authentication
        self.comminication_key = SSHKeys()

        ssh_private_key_02 = self.comminication_key.private_key
        ssh_public_key_02 = self.comminication_key.public_key

        with open(AppConfig.mos_ssh_priv_key_dir + "/" + self.template + '-' + vm_name + "-id_rsa", 'w') as content_file:
                content_file.write(ssh_private_key_02)

        with open(self.chroot_ssh_dir + "/authorized_keys", 'w') as content_file:
                content_file.write(ssh_public_key_02)

        os.chown(AppConfig.mos_ssh_priv_key_dir + "/" + self.template + '-'+ vm_name + "-id_rsa", self.running_uid, self.running_gid)
        os.chmod(AppConfig.mos_ssh_priv_key_dir + "/" + self.template + '-'+ vm_name + "-id_rsa", 0o0600)

        logging.info('Created SSH Keypair for VM: %s', vm_name)
        logging.info('Configured VM: %s ',
                vm_name)

    ## Build VM rootfs tar_file
    ## Used later by GuestFS for the QCOW image build
    def _rootfs_tar_build(self, vm_name: str):
        if os.path.exists(self.rootfs_tar):
            os.remove(self.rootfs_tar)
        else:
            pass

        tar = tarfile.open(self.rootfs_tar, "x:")

        os.chdir(self.chroot_dir)
        for i in os.listdir(self.chroot_dir):
            tar.add(i)
        tar.close()


    ## Bild VM rootfs QCOW image
    ## In accordance to build XML build parameters
    ## For now: Size, Free size
    def _rootfs_qcow_build(self, vm_name:str):
        vm = self.config.virtual_machines[vm_name]
        build_free_mb = vm.build_free_mb

        if os.path.exists(self.rootfs_img):
            os.remove(self.rootfs_img)
        else:
            pass

        self.rootfs_size_mb = os.path.getsize(self.rootfs_tar) / 1048576
        self.storage_mb = int(round(self.rootfs_size_mb + build_free_mb))

        g = guestfs.GuestFS(python_return_dict=True)

        g.disk_create(self.rootfs_img, "qcow2", self.storage_mb * 1024 * 1024 )
        # Enable for verbosity
        # g.set_trace(1)
        g.add_drive_opts(self.rootfs_img, format = "qcow2", readonly=0)
        g.launch()
        devices = g.list_devices()
        assert(len(devices) == 1)

        g.part_disk(devices[0], "gpt")
        partitions = g.list_partitions()
        assert(len(partitions) == 1)

        g.mkfs("ext4", partitions[0])
        g.mount(partitions[0], "/")

        g.tar_in(self.rootfs_tar, "/")

        g.shutdown()
        g.close()
        logging.info('Created QCOW image for VM: %s with %i MB size',
                vm_name, self.storage_mb)

        os.chown(self.rootfs_img, self.running_uid, self.running_gid)

class SSHKeys:
    def __init__(self):
        self.key = rsa.generate_private_key(
            backend=crypto_default_backend(), public_exponent=65537, key_size=2048)

        self.private_key = self.key.private_bytes(
            crypto_serialization.Encoding.PEM, crypto_serialization.PrivateFormat.TraditionalOpenSSL, crypto_serialization.NoEncryption()).decode("utf-8")

        self.public_key = self.key.public_key().public_bytes(
            crypto_serialization.Encoding.OpenSSH, crypto_serialization.PublicFormat.OpenSSH).decode("utf-8")
