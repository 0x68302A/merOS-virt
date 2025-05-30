#!/usr/bin/python3

import os
import distutils, distutils.dir_util
import tarfile
import subprocess
import glob
import time
import logging
import guestfs
import tempfile
import shutil
from typing import Dict, Optional, Tuple

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

from src.vm_models import VMConfig, Config, VirtualDisk
from src.app_config import AppConfig
from src.rootfs_manager import RootfsManager
from src.disk_manager import DiskManager

logger = logging.getLogger(__name__)

class VMBuilder:
    def __init__(self, config: Config, constellation: str, verbose: bool = False):
        self.config = config
        self.constellation = constellation
        self.disk_manager = DiskManager()

        try:
            self.running_uid = int(os.getenv('SUDO_UID'))
            self.running_gid = int(os.getenv('SUDO_GID'))
        except:
            None

        if verbose:
            logger.setLevel(logging.DEBUG)

        ## Source/ Configuration paths
        self.source_conf_dir = f"{AppConfig.mos_path}/constellations/{self.constellation}"
        self.source_conf_rootfs_common_dir = f"{self.source_conf_dir}/rootfs/common/includes.chroot"
        self.source_pkgs_dir = f"{self.source_conf_dir}/pkg/"



    def rootfs_image_build(self, vm_name: str):
        vm = self.config.virtual_machines[vm_name]
        logger.info(f"Building VM: {vm_name}")
        start_time = time.time()
        app_config = AppConfig()

        ## Chroot/ rootfs paths
        self.chroot_dir = f"{AppConfig.mos_path}/data/build/bootstrap/{self.constellation}/{vm_name}/"
        self.chroot_hooks_dir = f"{self.chroot_dir}/tmp/src/hooks"
        self.chroot_pkgs_dir = f"{self.chroot_dir}/opt"
        self.chroot_ssh_dir = f"{self.chroot_dir}/etc/ssh"

        ## Build paths
        self.rootfs_tar = f"{AppConfig.mos_path}/data/build/bootstrap/{self.constellation}/{vm_name}.tar"
        self.dest_image_path = f"{AppConfig.mos_disk_dir}/{self.constellation}-{vm_name}.qcow2"

        try:
            # Prepare rootfs
            self._rootfs_manage(vm_name, vm.distribution, vm.arch)
            self._chroot_configure(vm_name)
            self._ssh_keyadd(True, vm_name)
            logger.debug(f"Building tar for: {vm_name}")
            self._rootfs_tar_build(vm_name)
            logger.debug(f"Building qcow2 for: {vm_name}")
            self._rootfs_qcow_build(vm_name)

        except Exception as e:
            logger.error(f"Failed to build VM: {e}")
            raise

    def image_patch(self, vm_name: str, src_image_path: str):
        vm = self.config.virtual_machines[vm_name]
        disk = vm.disks[0]

        ## Constellation files
        source_conf_rootfs_dir = f"{self.source_conf_dir}/rootfs/{vm_name}/includes.chroot"
        source_hooks_dir = f"{self.source_conf_dir}/rootfs/{vm_name}/hooks"

        ## Build paths
        self.rootfs_tar = f"{AppConfig.mos_path}/data/build/bootstrap/{self.constellation}/{vm_name}.tar"
        self.dest_image_path = f"{AppConfig.mos_disk_dir}/{self.constellation}-{vm_name}.qcow2"

        ssh_keys = self._ssh_keyadd(False, vm_name)

        g = guestfs.GuestFS(python_return_dict=True)
        g_orig = guestfs.GuestFS(python_return_dict=True)

        start_time = time.time()

        try:

            ## Initialize & Analyze source image
            g_orig.add_drive_opts(str(src_image_path), format="qcow2", readonly=1)
            g_orig.launch()
            partitions = g_orig.list_partitions()

            rootfs = g_orig.inspect_os()
            rootfs_partition = rootfs[0]

            ## Clone image
            self.disk_manager.clone_qcow2(str(src_image_path), self.dest_image_path, vm.build_free_mb, rootfs_partition)

            ## Initialize & Configure destination image
            g.add_drive_opts(str(self.dest_image_path), format="qcow2", readonly=0)
            g.set_network(True)
            g.launch()

            devices = g.list_devices()
            if len(devices) == 0:
                raise RuntimeError("No devices found in the QCOW2 image")

            rootfs = g.inspect_os()
            rootfs_partition = rootfs[0]

            g.mount(rootfs_partition, "/")

            ## Perform rootfs operations
            try:
                self._copy_directory_to_guest_tar(g, f"{source_conf_rootfs_common_dir}", "/")
            except:
                logging.debug('No common rootfs for: %s', vm_name)

            logger.debug(f"Copying rootfs contents for VM: {vm_name}")
            self._copy_directory_to_guest_tar(g, f"{source_conf_rootfs_dir}", "/")
            self._copy_directory_to_guest_tar(g, f"{source_hooks_dir}", "/tmp/src/hooks")

            logger.debug(f"Configuring ssh keys for VM: {vm_name}")
            g.write("/etc/ssh/ssh_host_rsa_key", ssh_keys[0])
            g.write("/etc/ssh/authorized_keys", ssh_keys[1])

            logger.debug(f"Configuring VM: {vm_name}")
            g.command(["chmod", "0600", "/etc/ssh/ssh_host_rsa_key"])

            output = g.command(["sh", "-c", "for script in /tmp/src/hooks/*.chroot; do sh \"$script\"; done"])
            logging.debug(output)

            g.umount("/")
            g.sync()

            elapsed = time.time() - start_time
            logging.debug(f"Successfully patched QCOW image for VM: %s after {elapsed:.2f}s", vm_name)

        finally:
            ## Ensure we close the guestfs handles
            g_orig.shutdown()
            g_orig.close()

            g.shutdown()
            g.close()

    def _copy_directory_to_guest_tar(self, g, host_src_dir: str, guest_dest_dir: str):
        """
        Copies the *contents* of `host_src_dir` (not the dir itself) into `guest_dest_dir`.
        Uses tar-in for efficiency.
        """
        with tempfile.NamedTemporaryFile(suffix=".tar") as tmp_tar:
            with tarfile.open(tmp_tar.name, "w") as tar:
                # Add each item inside host_src_dir (not host_src_dir itself)
                for item in os.listdir(host_src_dir):
                    full_path = os.path.join(host_src_dir, item)
                    tar.add(full_path, arcname=item)

            ## Extract to guest_dest_dir (which must exist)
            g.mkdir_p(guest_dest_dir)  # Ensure target dir exists
            g.tar_in(tmp_tar.name, guest_dest_dir)

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

        self.source_conf_rootfs_dir = f"{self.source_conf_dir}/rootfs/{vm_name}/includes.chroot"
        self.source_hooks_dir = f"{self.source_conf_dir}/rootfs/{vm_name}/hooks"

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

        subprocess.run("/tmp/src/hooks/*.chroot", shell=True)
        os.chdir(f)
        os.chroot(".")

    def _ssh_keyadd(self, chroot: bool, vm_name: str):
        self.vm_name = vm_name

        ## Used for key_based authentication
        host_key = SSHKeys()
        communication_key = SSHKeys()

        ssh_privkey_01 = host_key.privkey

        ssh_privkey_02 = communication_key.privkey
        ssh_pubkey_02 = communication_key.pubkey

        ## PrivKey used by host
        with open(AppConfig.mos_ssh_priv_key_dir + "/" + self.constellation + '-' + vm_name + "-id_rsa", 'w') as content_file:
                content_file.write(ssh_privkey_02)

        os.chmod(AppConfig.mos_ssh_priv_key_dir + "/" + self.constellation + '-'+ vm_name + "-id_rsa", 0o0600)

        ## When --rootfs-only is used
        if chroot == True:
            with open(self.chroot_ssh_dir + "/ssh_host_rsa_key", 'w') as content_file:
                content_file.write(ssh_privkey_01)

            with open(self.chroot_ssh_dir + "/authorized_keys", 'w') as content_file:
                    content_file.write(ssh_pubkey_02)

            os.chmod(self.chroot_ssh_dir + "/ssh_host_rsa_key", 0o0600)

            os.chown(AppConfig.mos_ssh_priv_key_dir + "/" + self.constellation + '-'+ vm_name + "-id_rsa", self.running_uid, self.running_gid)

        ## When --use is used
        elif chroot == False:
            return ssh_privkey_01, ssh_pubkey_02

        logging.info('Created SSH Keypair for VM: %s', vm_name)
        logging.info('Configured VM: %s ',
                vm_name)

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


    def _rootfs_qcow_build(self, vm_name:str):
        vm = self.config.virtual_machines[vm_name]
        build_free_mb = vm.build_free_mb

        if os.path.exists(self.dest_image_path):
            os.remove(self.dest_image_path)
        else:
            pass

        self.rootfs_size_mb = os.path.getsize(self.rootfs_tar) / 1048576
        self.storage_mb = int(round(self.rootfs_size_mb + build_free_mb))

        g = guestfs.GuestFS(python_return_dict=True)

        g.disk_create(self.dest_image_path, "qcow2", self.storage_mb * 1024 * 1024 )
        # Enable for verbosity
        # g.set_trace(1)
        g.add_drive_opts(self.dest_image_path, format = "qcow2", readonly=0)
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

        os.chown(self.dest_image_path, self.running_uid, self.running_gid)

class SSHKeys:
    def __init__(self):
        self.key = rsa.generate_private_key(
            backend=crypto_default_backend(), public_exponent=65537, key_size=2048)

        self.privkey = self.key.private_bytes(
            crypto_serialization.Encoding.PEM, crypto_serialization.PrivateFormat.TraditionalOpenSSL, crypto_serialization.NoEncryption()).decode("utf-8")

        self.pubkey = self.key.public_key().public_bytes(
            crypto_serialization.Encoding.OpenSSH, crypto_serialization.PublicFormat.OpenSSH).decode("utf-8")
