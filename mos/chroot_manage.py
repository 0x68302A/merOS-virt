#!/usr/bin/python3

import mos
from mos.helper import *
from mos.bootstrap import *

import os
import sys
from shutil import *
import distutils
from distutils import *
from distutils import dir_util
import subprocess
from Crypto.PublicKey import RSA
import guestfs

target_chroot_conf_dir = mos.mos_path + "/conf/" + target_distro + "/" + mos.target_id + "/includes.chroot"
target_chroot_dir = mos.mos_path + "/data/build/bootstrap/" + target_distro + "/" + mos.target_id

target_ssh_dir = target_chroot_dir + "/etc/ssh"

target_rootfs_tar = mos.mos_path + "/data/build/vm_rootfs" + "/" + target_id + ".tar"
target_rootfs_img = mos.mos_img_dir + "/" + target_id + ".img"

target_size = 1.6
target_free_space = 0.4
target_storage = int(target_size + target_free_space)


def target_chroot_setup():

	if os.path.isdir(target_chroot_dir):
		None
	else:
		os.makedirs(target_chroot_dir, mode = 0o777, exist_ok = True)

		tar_file = tarfile.open(rootfs_targz)
		tar_file.extractall(target_chroot_dir)
		tar_file.close

	distutils.dir_util.copy_tree(target_chroot_conf_dir, target_chroot_dir)


def target_ssh_keys_gen():

	key = RSA.generate(2048)

	if not os.path.exists(target_ssh_dir):
		os.makedirs(target_ssh_dir)
	else:
		None

	## Write Target host key
	with open(target_ssh_dir + "/ssh_host_rsa_key", 'wb') as content_file:
		os.chmod(target_ssh_dir + "/ssh_host_rsa_key", 0o0600)
		content_file.write(key.exportKey('PEM'))

	## Write mos authentication pair
	with open(mos_ssh_priv_key_dir + "/" + mos.target_id + "-id_rsa", 'wb') as content_file:
		os.chmod(mos_ssh_priv_key_dir + "/" + mos.target_id + "-id_rsa", 0o0600)
		content_file.write(key.exportKey('PEM'))
		pubkey = key.publickey()
	with open(target_ssh_dir + "/authorized_keys", 'wb') as content_file:
		content_file.write(pubkey.exportKey('OpenSSH'))


def target_chroot_configure():
	os.chroot(target_chroot_dir)
	with open("/etc/resolv.conf", 'w') as file:
		file.write("nameserver " + default_gw + "\n")

	subprocess.run("/root/0100-conf.chroot", shell=True)
	subprocess.run("/root/0150-packages.chroot", shell=True)

## TODO ssh-keygen -f "/home/$USER_ID/.ssh/known_hosts" -R "[10.0.4.4]:2022" TODO

def target_rootfs_tar_build():
	print(target_rootfs_tar)
	print(target_chroot_dir)
#	os.remove(target_rootfs)
	os.chdir(target_chroot_dir)
	tar = tarfile.open(target_rootfs_tar, "x:")
	for i in os.listdir(target_chroot_dir):
		tar.add(i)
	tar.close()

def target_rootfs_qcow_build():
#	os.remove(target_img)
	g = guestfs.GuestFS(python_return_dict=True)

	g.disk_create(target_rootfs_img, "qcow2", 1024 * target_storage * 1024 * 1024)
	g.set_trace(1)
	g.add_drive_opts(target_rootfs_img, format = "qcow2", readonly=0)
	g.launch()
	devices = g.list_devices()
	assert(len(devices) == 1)

	g.part_disk(devices[0], "gpt")
	partitions = g.list_partitions()
	assert(len(partitions) == 1)

	g.mkfs("ext4", partitions[0])
	g.mount(partitions[0], "/")

	g.tar_in(target_rootfs_tar, "/")

	g.shutdown()
	g.close()
	print("done")

	os.chown(target_rootfs_img, uid, gid)
