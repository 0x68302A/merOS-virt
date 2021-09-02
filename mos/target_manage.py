#!/usr/bin/python3

import mos.helper as helper
import mos.target_get as target_get

import os
import sys
from shutil import *
import distutils
from distutils import *
from distutils import dir_util
import tarfile
import subprocess
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
import guestfs


class TargetManage:
	def __init__(self, target_full_id):
		self.target_full_id = target_full_id

		h = helper.Helper()
		self.h = h
		self.mos_path  =  h.mos_path
		self.arch = h.arch

		self.mos_img_dir = self.h.mos_img_dir
		self.mos_ssh_priv_key_dir = self.h.mos_ssh_priv_key_dir
		self.target_rootfs_img = self.mos_img_dir + "/" + self.target_full_id + ".img"


		self.target_id_split = self.target_full_id.split("-")
		self.target_fam = self.target_id_split[0]
		self.target_id = self.target_id_split[1]

		self.target_distro = "alpine"
		self.default_gw = h.default_gw

		self.target_chroot_conf_dir = self.mos_path + "/conf/target/" + self.target_fam + "/rootfs/" + self.target_id + "/includes.chroot"
		self.target_chroot_dir = self.mos_path + "/data/build/bootstrap/" + self.target_fam + "/" + self.target_id
		self.target_ssh_dir = self.target_chroot_dir + "/etc/ssh"

		self.mos_bootstrap_dir = self.mos_path + "/data/build/bootstrap"
		self.distro_rootfs_targz = self.mos_bootstrap_dir + "/" + "rootfs" + "_" + self.target_distro + "_" + self.arch + ".tar.gz"
		self.target_rootfs_tar = self.mos_path + "/data/build/bootstrap" + "/" + self.target_fam + "/" + self.target_id + ".tar"
		

		self.target_id_xml = self.mos_path + "/conf/target/" + self.target_fam + "/build/" + self.target_id + ".xml"

		self.DNS1 = "1.1.1.1"
		self.DNS2 = "1.0.0.1"

	def chroot_unpack(self):

		if os.path.exists(self.target_chroot_dir + "/sbin/init"):
			None
		else:
			os.makedirs(self.target_chroot_dir, mode = 0o777, exist_ok = True)
			
			tar_file = tarfile.open(self.distro_rootfs_targz)
			tar_file.extractall(self.target_chroot_dir)
			tar_file.close


	def chroot_configure(self):		

		distutils.dir_util.copy_tree(self.target_chroot_conf_dir, self.target_chroot_dir)
		f = os.open("/", os.O_PATH)
		os.chdir(self.target_chroot_dir)
		os.chroot(".")
		with open("/etc/resolv.conf", 'w') as file:
				file.write("nameserver " + self.default_gw + "\n")
		
		# subprocess.run("id", shell=True)
		subprocess.run("/root/0100-conf.chroot", shell=True)
		subprocess.run("/root/0150-packages.chroot", shell=True)
		os.chdir(f)
		os.chroot(".")


	def chroot_keyadd(self):
		self.hkkg = SSHKeys()
		ssh_private_key_01 = self.hkkg.private_key

		self.aukg = SSHKeys()
		ssh_private_key_02 = self.aukg.private_key
		ssh_public_key_02 = self.aukg.public_key

		with open(self.target_ssh_dir + "/ssh_host_rsa_key", 'w') as content_file:
			content_file.write(ssh_private_key_01)

		with open(self.mos_ssh_priv_key_dir + "/" + self.target_full_id + "-id_rsa", 'w') as content_file:
			content_file.write(ssh_private_key_02)
			
		with open(self.target_ssh_dir + "/authorized_keys", 'w') as content_file:
					content_file.write(ssh_public_key_02)
			
		os.chmod(self.target_ssh_dir + "/ssh_host_rsa_key", 0o0600)
		os.chmod(self.mos_ssh_priv_key_dir + "/" + self.target_full_id + "-id_rsa", 0o0600)

	def rootfs_tar_build(self):
		if os.path.exists(self.target_rootfs_tar):
			os.remove(self.target_rootfs_tar)
		else:
			pass

		tar = tarfile.open(self.target_rootfs_tar, "x:")

		os.chdir(self.target_chroot_dir)
		for i in os.listdir(self.target_chroot_dir):
			tar.add(i)
		tar.close()


	def rootfs_qcow_build(self):
		if os.path.exists(self.target_rootfs_img):
			os.remove(self.target_rootfs_img)
		else:
			pass

		self.xml_parse = helper.ParseXML(self.target_id_xml)

		self.target_rootfs_size_mb = os.path.getsize(self.target_rootfs_tar) / 1048576
		self.target_free_space_mb = float(self.xml_parse.read_xml_value("size", "free_space_mb"))
		self.target_storage_mb = int(round(self.target_rootfs_size_mb + self.target_free_space_mb))
		print(self.target_free_space_mb)
		print(self.target_storage_mb)


		g = guestfs.GuestFS(python_return_dict=True)

		g.disk_create(self.target_rootfs_img, "qcow2", self.target_storage_mb * 1024 * 1024 )
		# g.set_trace(1)
		g.add_drive_opts(self.target_rootfs_img, format = "qcow2", readonly=0)
		g.launch()
		devices = g.list_devices()
		assert(len(devices) == 1)

		g.part_disk(devices[0], "gpt")
		partitions = g.list_partitions()
		assert(len(partitions) == 1)

		g.mkfs("ext4", partitions[0])
		g.mount(partitions[0], "/")

		g.tar_in(self.target_rootfs_tar, "/")

		g.shutdown()
		g.close()
		print("done")

		os.chown(self.target_rootfs_img, self.h.uid, self.h.gid)


	def chroot_setup(self):
		tm  = TargetManage(self.target_full_id)
		tm.chroot_unpack()
		tm.chroot_configure()
		tm.chroot_keyadd()


	def rootfs_build(self):
		tm  = TargetManage(self.target_full_id)
		tm.rootfs_tar_build()
		tm.rootfs_qcow_build()


class SSHKeys:
	def __init__(self):
		self.key = rsa.generate_private_key(
			backend=crypto_default_backend(), public_exponent=65537, key_size=2048)
		
		self.private_key = self.key.private_bytes(
			crypto_serialization.Encoding.PEM, crypto_serialization.PrivateFormat.PKCS8, crypto_serialization.NoEncryption()).decode("utf-8")
		
		self.public_key = self.key.public_key().public_bytes(
			crypto_serialization.Encoding.OpenSSH, crypto_serialization.PublicFormat.OpenSSH).decode("utf-8")
"""
TODO ssh-keygen -f "/home/$USER_ID/.ssh/known_hosts" -R "[10.0.4.4]:
"""
