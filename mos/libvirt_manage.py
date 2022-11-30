#!/usr/bin/python3

import mos.helper as helper

import glob
import libvirt
import sys
import time
import re
import subprocess
import logging
import os


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


	def dom_init(self):

		self.target_id_split = re.split('\/|\-|\.|_', self.target_fam_id)
		self.fam_id = self.target_id_split[-2]

		self.no_mos_target_split = re.split('\/|\-|\_', self.target_fam_id)
		print(self.no_mos_target_split)
		self.no_mos_target = ('dom_' + self.no_mos_target_split[0]
						+ '-' + self.no_mos_target_split[1]
						+ '-' + self.no_mos_target_split[2])

		self.conf_dir = self.mos_path + "/conf/target/" + 'mos_' + self.fam_id + "/libvirt/"

		self.dom = self.conf_dir + self.no_mos_target + ".xml"

		try:

			## Grab target_id from libvirt XML filename
			self.xml_id = re.split('\/|\_|\.', self.dom)
			self.target_id = self.xml_id[-1]
			self.target_full_id = 'mos_' + self.target_id
			print(self.target_full_id)

			self.target_rootfs_img = ( self.mos_img_dir + '/'
						+ self.target_full_id +  ".img" )

			with open(self.dom, 'r') as file :
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

				logging.info("Configured Target '%s'\n--From: '%s'" % (dom0.name(), i))

			except libvirt.libvirtError:
				logging.error('Domain is running, or Failed to Parse XML')



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
				self.xml_network_data = self.xml_network_data.replace('$NETWORK_FULL_ID',
											self.network_full_id)

				dom0 = self.conn.networkCreateXML(self.xml_network_data)
				logging.info("Configured Network Interface '%s'\n--From %s" % (self.network_full_id, i))

			except libvirt.libvirtError:
				logging.error('Network is running, Target Image is missing, or Failed to Parse XML')


	## Run Family- specific Hooks
	## Mainly in regards to Networking
	def hooks_init(self):
		self.hooks = glob.glob(self.hooks_dir + "*")
		for i in self.hooks:
			try:
				subprocess.call(i)
				logging.info('Executed Host Hooks\n--From %s', i)

			except CalledProcessError:
				logging.error(CalledProcessError)

## Terminate All Libvrit Domains
## TODO: Create a method to allow for Target-Specific Termination
class LibvirtExtra:
	def __init__(self):


		## Import Global Variables
		h = helper.Helper()
		self.h = h
		self.mos_path  =  h.mos_path
		self.conf_dir = self.mos_path + "/conf/target"
		self.img_dir = self.mos_path + "/data/images"

		self.conn = libvirt.open("qemu:///system")

	def libvirt_info(self, Full=True):

		if Full == True:

			print("Available Families:")

			dir_list = os.listdir(self.conf_dir)
			print('   '+str(dir_list))

			print("Availabe Targets:")
			Targets_list = []

			for (root, dirs, file) in os.walk(self.img_dir):
				for f in file:
					if '.img' in f:
						f = re.split('\/|\.', f)
						f = f[-2]
						print('   '+f)




		print("Active Targets:")

		domains = self.conn.listAllDomains(1)
		if len(domains) != 0:
			for domain in domains:
				print('   '+domain.name())
		else:
			print('  None')


		print("Active Networks:")
		networks = self.conn.listAllNetworks(2)
		if len(networks) != 0:
			for network in networks:
				print('   '+network.name())
		else:
			print('  None')

		self.conn.close()
		exit(0)



	def shutdown_target(self, TargetID):

		try:
			domName = self.conn.lookupByName(TargetID)
			domID = domName.ID()

			dom = self.conn.lookupByID(domID)
			dom.destroy()
			time.sleep(1)


		except libvirt.libvirtError:
			logging.error('Failed to find the Target specified')
			sys.exit(1)

		logging.info("Target %s shut-down" % TargetID )


	def shutdown_all(self):

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
			logging.info('merOS shut down all Libvirt guests gracefully')
