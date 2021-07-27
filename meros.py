#!/usr/bin/python3

import mos
from mos import *
from mos.helper import *
import subprocess

import getopt
import sys

def main():

	try:
		opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help","setup","kernel-build","bootstrap","build","run","shutdown","output="])
	except getopt.GetoptError as err:
        	# print help information and exit:
		print(err)  # will print something like "option -a not recognized"
		display_help()
		sys.exit(2)
	output = None
	verbose = False
	for o, a in opts:
		if o == "-v":
			verbose = True
		elif o in ("-h", "--help"):
			display_help()
			sys.exit()
		elif o in ("--setup"):
			mos.host_tree_conf()
			mos.run_as_root(print("Running as root"))
			mos.run_as_root(mos.host_apt_conf())
			mos.run_as_root(mos.host_grub_conf())
			mos.run_as_root(mos.host_syslink())
			sys.exit()
		elif o in ("--kernel-build"):
			mos.kernel_build()
			sys.exit()
		elif o in ("--build"):
			target_id = sys.argv[2]
			print("Building:", target_id)
			mos.target_bootstrap()
			mos.target_chroot_setup()
			mos.target_ssh_keys_gen()
			mos.target_chroot_configure()
			mos.target_rootfs_tar_build()
			mos.target_rootfs_qcow_(build)
			sys.exit()
		elif o in ("--run"):
			mos.run_as_root(print("Running as root"))
			mos.run_as_root(mos.vm_init())
			mos.run_as_root(mos.net_init())
		elif o in ("--shutdown"):
			mos.run_as_root(print("Running as root"))
			mos.run_as_root(mos.vm_shutdown_all())
		elif o in ("-o", "--output"):
			output = a
		else:
			print("Error")
#			assert False, "unhandled option"

if __name__ == "__main__":
	main()



'''
--net-access)

	root_check

	declare BR_ID=$2.BR

	sys_nftables_net_access $BR_ID

	exit 0
;;
-c|--connect)

	declare VM_ID=$2

	source_vm_var
	ssh_connect

	exit 0
;;
-p|--push)

	declare FILE=$2
	declare VM_ID=$3

	ssh_push

	exit 0
;;
--pull)

	declare VM_ID=$2

	ssh_pull

	exit 0
	;;
--sync)

	declare VM_ID=$2

	ssh_sync

	exit 0
;;
--clean)

	root_check

	rm -rf $MOS_PATH/etc/build/kernel/*
	rm -rf $MOS_PATH/etc/build/bootstrap/*

	exit 0
;;
'''
