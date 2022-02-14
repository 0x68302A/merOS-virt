#!/usr/bin/python3

import mos.helper as helper
import mos.rootfs_get as rootfs_get
import mos.kernel_build as kernel_build

import os
import sys
import pwd
import distutils, distutils.dir_util
import tarfile
import subprocess
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
import guestfs
import glob

import logging

## We will by initializing 
## all necessary variables and parameters
class TargetManage:
	def __init__(self, family_id):
		self.family_id = family_id
		logging.info('Target Family is %s', self.family_id)

		h = helper.Helper()
		self.h = h
		self.mos_path  =  h.mos_path
		self.arch = h.arch

		self.mos_ssh_priv_key_dir = self.h.mos_ssh_priv_key_dir
		self.default_gw = h.default_gw
		self.target_conf_dir = self.mos_path + "/conf/target/" + self.family_id
		self.target_chroot_common_dir =	self.target_conf_dir + "/rootfs/common/includes.chroot"
		self.mos_bootstrap_dir = self.mos_path + "/data/build/bootstrap"

		self.user_name = os.getenv("SUDO_USER")
		self.pwnam = pwd.getpwnam(self.user_name)

		self.uid = self.pwnam.pw_uid
		self.gid = self.pwnam.pw_gid

		## The target DNS parameters
		## for now hardcoded
		## TODO: Parse them from XML
		self.DNS1 = "1.1.1.1"
		self.DNS2 = "1.0.0.1"

	## Get, Unpack, and Place rootfs
	def rootfs_manage(self):

		## Check for init, and skip download if found
		## TODO: add an update flag to --build
		## As to allow for updating the base rootfs

		if os.path.exists(self.target_chroot_dir + "/sbin/init"):
			None
			logging.info('Chroot is already populated with /sbin/init - Skipping rootfs download')
		else:

			logging.info('Processing rootfs requirments')

			tg = rootfs_get.RootfsGet(self.target_distro)
			tg.get_rootfs()

			os.makedirs(self.target_chroot_dir, mode = 0o777, exist_ok = True)

			## Check whether we're dealing with a
			## tar.gz ROOTFS of a common Path

			if os.path.isfile(self.distro_rootfs_targz):
				tar_file = tarfile.open(self.distro_rootfs_targz)
				tar_file.extractall(self.target_chroot_dir)
				tar_file.close

			elif os.path.exists(self.distro_rootfs_dir):
				self.cp_args = ('cp -rn '
					+ self.distro_rootfs_dir
					+ '/* ' + self.target_chroot_dir)
				subprocess.run(self.cp_args, shell=True)
				## distutils.dir_util.copy_tree(self.distro_rootfs_dir, self.target_chroot_dir, preserve_symlinks=True)

			else:
				logging.info('Can not find distro ROOTFS')


	## Configure the above rootfs
	## In a Chroot enviroment
	def chroot_configure(self):

		## Copy Family-Common rootfs base
		try:
			distutils.dir_util.copy_tree(self.target_chroot_common_dir, self.target_chroot_dir)
		except:
			logging.info('No common rootfs Configuration found')
		
		## Copy Target-Specific rootfs base
		distutils.dir_util.copy_tree(self.target_chroot_conf_dir, self.target_chroot_dir)
		## Copy Target-Specific hooks
		distutils.dir_util.copy_tree(self.target_hooks_conf_dir, self.target_hooks_dir)

		## Chroot to Target
		f = os.open("/", os.O_PATH)
		os.chdir(self.target_chroot_dir)

		os.chroot(".")
		
		## Write DNS settings to Target
		with open("/etc/resolv.conf", 'w') as file:
				file.write("nameserver " + self.default_gw + "\n")

		## Execute Target-Specific Configuration hooks
		subprocess.run("/tmp/mos/hooks/0100-conf.chroot", shell=True)
		subprocess.run("/tmp/mos/hooks/0150-packages.chroot", shell=True)
		os.chdir(f)
		os.chroot(".")

	## Create and place SSH-keys
	def chroot_keyadd(self):

		## Used for Target ssh_host_rsa_key
		self.host_key = SSHKeys()
		ssh_private_key_01 = self.host_key.private_key

		with open(self.target_ssh_dir + "/ssh_host_rsa_key", 'w') as content_file:
			content_file.write(ssh_private_key_01)

		os.chmod(self.target_ssh_dir + "/ssh_host_rsa_key", 0o0600)

		## Used for Key_based authentication
		self.comminication_key = SSHKeys()

		ssh_private_key_02 = self.comminication_key.private_key
		ssh_public_key_02 = self.comminication_key.public_key

		with open(self.mos_ssh_priv_key_dir + "/" + self.family_id + '-' + self.target_id + "-id_rsa", 'w') as content_file:
				content_file.write(ssh_private_key_02)

		with open(self.target_ssh_dir + "/authorized_keys", 'w') as content_file:
				content_file.write(ssh_public_key_02)

		os.chown(self.mos_ssh_priv_key_dir + "/" + self.family_id + '-'+ self.target_id + "-id_rsa", self.uid, self.gid)
		os.chmod(self.mos_ssh_priv_key_dir + "/" + self.family_id + '-'+ self.target_id + "-id_rsa", 0o0600)

		logging.info('Created SSH Keypair for Target: %s', self.target_id)
		logging.info('Configured Target: %s ',
				self.target_id)

	## Build Target rootfs tar_file
	## Used later by GuestFS for the QCOW image build
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


	## Bild Target rootfs QCOW image
	## In accordance to build XML build parameters
	## For now: Size, Free size
	def rootfs_qcow_build(self):
		if os.path.exists(self.target_rootfs_img):
			os.remove(self.target_rootfs_img)
		else:
			pass

		self.target_rootfs_size_mb = os.path.getsize(self.target_rootfs_tar) / 1048576
		self.target_free_space_mb = float(self.xml_parse.read_xml_value("size", "free_space_mb"))
		self.target_storage_mb = int(round(self.target_rootfs_size_mb + self.target_free_space_mb))

		g = guestfs.GuestFS(python_return_dict=True)

		g.disk_create(self.target_rootfs_img, "qcow2", self.target_storage_mb * 1024 * 1024 )
		# Enable for verbosity
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
		logging.info('Created QCOW image for Target: %s with %i MB size',
				self.target_id, self.target_storage_mb)

		os.chown(self.target_rootfs_img, self.h.uid, self.h.gid)

	## Define Target-Specific variables and parameters
	## Also conntains kernel_build
	def main(self):

		if self.h.euid != 0:
			print('We need root access to build.')
			args = ['sudo', sys.executable] + sys.argv + [os.environ]
			os.execlpe('sudo', *args)

		# for self.target_xml in self.target_xmls:
		self.target_xmls = glob.glob(self.mos_path
					+ '/conf/target/'
					+ self.family_id
					+ '/build/'
					+ '*.xml')

		for self.target_xml in self.target_xmls:

			self.target_xml_path = self.target_xml.split('/')
			self.xml_parse = helper.ParseXML(self.target_xml)

			self.target_id = str(self.xml_parse.read_xml_value("build", "id"))

			logging.info('Found target XML %s', self.target_xml)
			logging.info('Target ID is %s', self.target_id)

			self.target_distro = str(self.xml_parse.read_xml_value("build", "distro"))

			self.distro_rootfs_targz = (self.mos_bootstrap_dir
								+ "/" + "rootfs"
								+ "_" + self.target_distro
								+ "_" + self.arch + ".tar.gz")

			self.distro_rootfs_dir = (self.mos_bootstrap_dir
								+ "/" + "rootfs"
								+ "_" + self.target_distro
								+ "_" + self.arch)

			logging.info('Target distro is %s', self.target_distro)

			## Target chroot Template directory
			self.target_chroot_conf_dir = os.path.join(self.target_conf_dir
									+ '/rootfs/'
									+ self.target_id
									+ '/includes.chroot')

			## Target chroot/ rootfs build directory
			self.target_chroot_dir = os.path.join(self.mos_path
									+ '/data/build/bootstrap/'
									+ self.family_id + '/'
									+ self.target_id)

			## Target hooks ( Build-Time executed code )
			self.target_hooks_conf_dir = os.path.join(self.target_conf_dir
									+ '/rootfs/'
									+ self.target_id
									+ '/hooks')
			## Target hooks location in Target ROOTFS
			self.target_hooks_dir = self.target_chroot_dir + '/tmp/mos/hooks'

			## Target SSH Configuration directory
			self.target_ssh_dir = os.path.join(self.target_chroot_dir + '/etc/ssh')

			self.target_rootfs_tar = (self.mos_path
							+ '/data/build/bootstrap/'
							+ self.family_id + '/'
							+ self.target_id + '.tar')

			## Host images ( Built ROOTFS ) directory
			self.mos_img_dir = self.h.mos_img_dir

			self.target_rootfs_img = (self.mos_img_dir + '/'
							+ self.family_id + '-'
							+ self.target_id + '.img')


			logging.info('ECHO %s' ,self.xml_parse.read_xml_value("build", "kernel"))
			if str(self.xml_parse.read_xml_value("build", "kernel")) == 'yes':
				logging.info('Cloning and build the Linux kernel')
				self.kb = kernel_build.KernelBuild()
				self.kb.kernel_clone()
				self.kb.kernel_build()
			else:
				pass

			self.rootfs_manage()
			self.chroot_configure()
			self.chroot_keyadd()
			self.rootfs_tar_build()
			self.rootfs_qcow_build()

## SSH key generation Class
## Needed for storing the different pairs Safely
class SSHKeys:
	def __init__(self):
		self.key = rsa.generate_private_key(
			backend=crypto_default_backend(), public_exponent=65537, key_size=2048)

		self.private_key = self.key.private_bytes(
			crypto_serialization.Encoding.PEM, crypto_serialization.PrivateFormat.TraditionalOpenSSL, crypto_serialization.NoEncryption()).decode("utf-8")

		self.public_key = self.key.public_key().public_bytes(
			crypto_serialization.Encoding.OpenSSH, crypto_serialization.PublicFormat.OpenSSH).decode("utf-8")
