#!/usr/bin/python3

import mos.helper as helper

import glob
import libvirt
import sys
import time
import re
import subprocess
import logging

class LibvirtManage:
	def __init__(self, target_fam_id):

		self.target_fam_id = target_fam_id

		## Import Global Variables
		h = helper.Helper()
		self.h = h
		self.mos_path  =  h.mos_path
		self.arch = h.arch

		self.mos_img_dir = self.h.mos_img_dir
		self.mos_ssh_priv_key_dir = self.h.mos_ssh_priv_key_dir
		self.kernel_img = self.mos_img_dir + "/bzImage"

		self.conf_dir = self.mos_path + "/conf/target/" + self.target_fam_id
		self.xml_dir = self.conf_dir + "/libvirt/"
		self.hooks_dir = self.conf_dir + "/hooks/"

		## Connect to Hypervisor
		try:
			self.conn = libvirt.open("qemu:///system")

		except libvirt.libvirtError:
			logging.error('Failed to open connection to the hypervisor')
			sys.exit(1)

	def doms_init(self):

		## For every domain XML found
		self.doms = glob.glob(self.xml_dir + "dom_*")
		for i in self.doms:
			try:

				## Grab target_id from libvirt XML filename
				self.xml_id = re.split('\/|\_|\.', i)
				self.target_id = self.xml_id[-2]
				self.target_full_id = 'mos_' + self.target_id

				self.target_rootfs_img = ( self.mos_img_dir + '/'
							+ self.target_full_id +  ".img" )

				with open(i, 'r') as file :
					self.xml_domain_data = file.read()

				## Change custom libvirt options
				self.xml_domain_data = self.xml_domain_data.replace('$TARGET_FULL_ID', self.target_full_id)
				self.xml_domain_data = self.xml_domain_data.replace('$KERNEL_IMG', self.kernel_img)
				self.xml_domain_data = self.xml_domain_data.replace('$TARGET_ROOTFS_IMG', self.target_rootfs_img)

				dom0 = self.conn.createXML(self.xml_domain_data)

			except libvirt.libvirtError:
				logging.error('Domain is running, or Failed to Parse XML')

			logging.info("Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType()))
			logging.info(dom0.info())


	def nets_init(self):
		self.nets = glob.glob(self.xml_dir + "net_*")
		for i in self.nets:

			try:

				## Define naming schema
				self.xml_id = re.split('\/|\_|\.', i)
				self.network_id = self.xml_id[-2]
				self.network_full_id = 'mos_' + self.network_id

				with open(i, 'r') as file :
					self.xml_network_data = file.read()

				## Change custom libvirt options
				self.xml_network_data = self.xml_network_data.replace('$NETWORK_FULL_ID', self.network_full_id)

				dom0 = self.conn.networkCreateXML(self.xml_network_data)
				logging.info('Created Network interface from %s', i)

			except libvirt.libvirtError:
				logging.error('Network is running, Target Image is missing, or Failed to Parse XML')


	## Run Family- specific Hooks
	## Mainly in regards to Networking
	def hooks_init(self):
		self.hooks = glob.glob(self.hooks_dir + "*")
		for i in self.hooks:
			try:
				subprocess.call(i)
				logging.info('Applied netfilter rules from %s', i)

			except CalledProcessError:
				logging.error(CalledProcessError)

## Terminate All Libvrit Domains
## TODO: Create a method to allow for Target-Specific Termination
class LibvirtTerminate:
	def __init__(self):

		self.conn = libvirt.open("qemu:///system")

		for i in self.conn.listDomainsID():
				self.dom = self.conn.lookupByID(i)
				self.dom.destroy()
				time.sleep(1)

		for i in self.conn.listNetworks():
				self.net = self.conn.networkLookupByName(i)
				self.net.destroy()
				time.sleep(1)

		if self.conn.listDomainsID():
			logging.error('ERROR! There are live domains.')
		else:
			logging.info('merOS shut down gracefully')


	def vm_shutdown(self):

		xml2str(xml_id)
		libvirt_conn()
		try:
			dom = conn.lookupByID(xml_id)
			dom0 = conn.destroy(dom)
		except libvirt.libvirtError:
			logging.error('Failed to find the main domain')
			sys.exit(1)

		logging.info(("Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType())))
		logging.info((dom0.info()))
