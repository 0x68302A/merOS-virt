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
	def __init__(self, target_full_id):
		self.target_full_id = target_full_id
		h = helper.Helper()
		self.h = h
		self.mos_path  =  h.mos_path
		self.arch = h.arch

		self.mos_img_dir = self.h.mos_img_dir
		self.target_rootfs_img = self.mos_img_dir + self.target_full_id + ".img"
		self.mos_ssh_priv_key_dir = self.h.mos_ssh_priv_key_dir
		self.kernel_img = self.mos_img_dir + "bzImage"

		try:
			self.target_id_split = self.target_full_id.split("-")
			self.target_fam = self.target_id_split[0]
			self.target_id = self.target_id_split[1]
		except:
			self.target_fam = self.target_full_id

		self.conf_dir = self.mos_path + "/conf/target/" + self.target_fam
		self.xml_dir = self.conf_dir + "/libvirt/"
		self.hooks_dir = self.conf_dir + "/hooks/"

		try:
			self.conn = libvirt.open("qemu:///system")
		except libvirt.libvirtError:
			logging.error('Failed to open connection to the hypervisor')
			sys.exit(1)


	def doms_init(self):
		self.doms = glob.glob(self.xml_dir + "dom_*")
		for i in self.doms:
			try:
				self.xml_id = re.split('\/|\_|\.', i)
				self.target_id = self.xml_id[-2]

				self.target_rootfs_img = ( self.mos_img_dir
							+ self.target_id + ".img" )

				self.xml_parse = helper.ParseXML(i)
				self.xml = self.xml_parse.edit_xml("kernel", self.kernel_img)
				self.xml = self.xml_parse.edit_xml("devices/disk/source", self.target_rootfs_img, attribute="file")
				dom0 = self.conn.createXML(self.xml)
			except libvirt.libvirtError:
				logging.error('Domain is running, or Failed to Parse XML')

			logging.info("Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType()))
			logging.info(dom0.info())


	def nets_init(self):
		self.nets = glob.glob(self.xml_dir + "net_*")
		for i in self.nets:
			try:
				self.xml_parse = helper.ParseXML(i)
				self.xml = self.xml_parse.read_xml()
				dom0 = self.conn.networkCreateXML(self.xml)
			except libvirt.libvirtError:
				logging.error('Network is running, or Failed to Parse XML')


	def hooks_init(self):
		self.hooks = glob.glob(self.hooks_dir + "*")
		for i in self.hooks:
			try:
				subprocess.call(i)
			except CalledProcessError:
				logging.error(CalledProcessError)

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
