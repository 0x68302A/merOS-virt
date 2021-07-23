#!/usr/bin/python3

import mos
from mos import *

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
			mos.runAsRoot(print("Running as root"))
			mos.runAsRoot(mos.sys_apt_conf())
			mos.runAsRoot(mos.sys_grub_conf())
			mos.runAsRoot(mos.sys_link_set())
			sys.exit()
		elif o in ("--kernel-build"):
			mos.kernel_build()
			sys.exit()
		elif o in ("--build"):
			build_id = sys.argv[2]
			print("Building:", build_id)

			mos.bootstrap()
			mos.chroot_build()
			mos.gen_keys()
			mos.runAsRoot(print("merOS"))
			mos.runAsRoot(mos.chroot_configure())
			mos.packRootfs()
			mos.buildRootfs() # TODO Drop Priveleges, BETTER permissions management
			sys.exit()
		elif o in ("--run"):
			mos.runAsRoot(print("Running as root"))
			mos.runAsRoot(mos.vm_init())
			mos.runAsRoot(mos.net_init())
		elif o in ("--shutdown"):
			mos.runAsRoot(print("Running as root"))
			mos.runAsRoot(mos.vm_shutdown_all())
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
