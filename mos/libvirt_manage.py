#!/usr/bin/python3

import mos.helper as helper

import glob
import libvirt
import sys
import time


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
		
		self.target_id_split = self.target_full_id.split("-")
		self.target_fam = self.target_id_split[0]
		self.target_id = self.target_id_split[1]
		
		self.xml_dir = self.mos_path + "/conf/target/" + self.target_fam + "/libvirt/"
		
		
		try:
			self.conn = libvirt.open("qemu:///system")
		except libvirt.libvirtError:
			print('Failed to open connection to the hypervisor')
			sys.exit(1)


	def doms_init(self):
		self.doms = glob.glob(self.xml_dir + "/dom_*")
		for i in self.doms:
			try:
				self.xml_parse = helper.ParseXML(i)
				self.edit_xml = self.xml_parse.edit_xml("kernel", self.kernel_img)
				self.edit_xml = self.xml_parse.edit_xml("file", self.target_rootfs_img)
				self.edit_xml = self.xml_parse.edit_xml("devices/disk/source", self.target_rootfs_img, attribute="file")
				# print(self.edit_xml)
				dom0 = self.conn.createXML(self.edit_xml)
			except libvirt.libvirtError:
				print('Failed to Parse XML')
				sys.exit(1)
	
			print("Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType()))
			print(dom0.info())


	def nets_init(self):
		self.nets = glob.glob(self.xml_dir + "/net_*")
		for i in self.nets:
			try:
				dom0 = self.conn.networkCreateXML(self.xml2str(i))
			except libvirt.libvirtError:
				print('Failed to Parse XML')
				sys.exit(1)


	def vm_shutdown_all(self):
		libvirt_conn()
		for i in conn.listDomainsID():
				dom = conn.lookupByID(i)
				dom.destroy()
				time.sleep(1)
		for i in conn.listNetworks():
				net = conn.networkLookupByName(i)
				net.destroy()
				time.sleep(1)
		if conn.listDomainsID():
			print('ERROR! There are live domains.')
		else:
			print('merOS shut down gracefully')
	
	
	def vm_shutdown(self):
	
		xml2str(xml_id)
		libvirt_conn()
		try:
			dom = conn.lookupByID(xml_id)
			dom0 = conn.destroy(dom)
		except libvirt.libvirtError:
			print('Failed to find the main domain')
			sys.exit(1)
	
		print("Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType()))
		print(dom0.info())
	
	
