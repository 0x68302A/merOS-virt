#!/usr/bin/python3

import mos

import libvirt
import sys
import time

xml_id = "mos_fw"

def xml_str(xml_id):
	xml_file = mos.mosPath + "/etc/conf/libvirt/" + xml_id + ".xml"
	global xml_data
	with open(xml_file, 'r') as file:
		xml_data = file.read().replace('\n', '')

def libvirt_conn():
	xml_str(xml_id)
	global conn
	try:
		conn = libvirt.open("qemu:///system")
	except libvirt.libvirtError:
		print('Failed to open connection to the hypervisor')
		sys.exit(1)

def vm_init():

	libvirt_conn()
	try:
		dom0 = conn.createXML(xml_data)
	except libvirt.libvirtError:
		print('Failed to Parse XML')
		sys.exit(1)

	print("Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType()))
	print(dom0.info())

def vm_shutdown_all():

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


def vm_shutdown():

	xml_str(xml_id)
	libvirt_conn()

	try:
		dom = conn.lookupByID(xml_id)
		dom0 = conn.destroy(dom)
	except libvirt.libvirtError:
		print('Failed to find the main domain')
		sys.exit(1)

	print("Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType()))
	print(dom0.info())

def net_init():

	xml_str("mos_pub_net")
	libvirt_conn
	try:
		dom0 = conn.networkCreateXML(xml_data)
	except libvirt.libvirtError:
		print('Failed to Parse XML')
		sys.exit(1)
