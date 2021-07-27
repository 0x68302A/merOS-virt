#!/usr/bin/python3

import mos
from mos import *

import guestfs

target_rootfs = mos.mos_path + "/data/build/vm_rootfs" + "/" + target_id + ".tar"
target_img = mos.mos_path + "/data/images" + "/" + target_id + ".img"

target_size = 1.6
target_free_space = 0.4
target_storage = int(target_size + target_free_space)

def packRootfs():
	os.remove(target_rootfs)
	tar = tarfile.open(target_rootfs, "w:")
	os.chdir(chrootDir)
	for name in os.listdir(chrootDir):
		tar.add(name)
	tar.close()

def buildRootfs():
	os.remove(target_img)
	g = guestfs.GuestFS(python_return_dict=True)

	g.disk_create(target_img, "qcow2", 1024 * target_storage * 1024 * 1024)
	g.set_trace(1)
	g.add_drive_opts(target_img, format = "qcow2", readonly=0)
	g.launch()
	devices = g.list_devices()
	assert(len(devices) == 1)

	g.part_disk(devices[0], "gpt")
	partitions = g.list_partitions()
	assert(len(partitions) == 1)

	g.mkfs("ext4", partitions[0])
	g.mount(partitions[0], "/")

	g.tar_in(target_rootfs, "/")

	g.shutdown()
	g.close()
	print("done")

	os.chown(target_img, uid, gid)
