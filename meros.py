#!/usr/bin/python3


import mos.helper as helper
import mos.kernel_build as kernel_build
import mos.host_conf as host_conf
import mos.target_get as target_get
import mos.target_manage as target_manage
import mos.libvirt_manage as libvirt_manage
import mos.ssh_communication as ssh_communication
import subprocess
import logging

import getopt
import sys


def main():
	h = helper.Helper
	mos_path = h.mos_path

	logging.basicConfig(
			filename = mos_path + '/LOG',
			format = '%(asctime)s::MerOS::%(levelname)s::%(message)s',
			datefmt = '%H:%M:%S',
			encoding = 'utf-8',
			level = logging.INFO)


	try:
		opts, args = getopt.getopt(sys.argv[1:], "hic:v", [
								"help", "setup",
								"kernel-build",
								"get", "bootstrap", "build",
								"init","shutdown",
								"connect","push", "pull",
								"output="
								])


	except getopt.GetoptError as err:
		print(err)
		h.display_help()
		sys.exit(2)
	output = None
	verbose = False

	for o, a in opts:
		if o == "-v":
			verbose = True

		elif o in ("-h", "--help"):
			h.display_help()
			sys.exit()

		elif o in ("--setup"):
			hc = host_conf.HostConf()
			hc.main()
			sys.exit()

		elif o in ("--kernel-build"):
			kb = kernel_build.KernelBuild()
			kb.kernel_clone()
			kb.kernel_build()
			sys.exit()

		elif o in ("--get"):
			target_distro = sys.argv[2]
			tg = target_get.TargetGet(target_distro)
			tg.get_rootfs()

		elif o in ("--build"):
			target_full_id = sys.argv[2]
			tm = target_manage.TargetManage(target_full_id)
			tm.chroot_unpack()
			tm.chroot_configure()
			tm.chroot_keyadd()
			tm.rootfs_tar_build()
			tm.rootfs_qcow_build()
			sys.exit()

		elif o in ("-i", "--init"):
			target_full_id = sys.argv[2]
			lm = libvirt_manage.LibvirtManage(target_full_id)
			lm.nets_init()
			lm.doms_init()
			lm.hooks_init()

		elif o in ("-c", "--connect"):
			target_full_id = sys.argv[2]
			tc = ssh_communication.SSHCommunication(target_full_id)
			tc.interactive_shell()

		elif o in ("--push"):
			target_full_id = sys.argv[2]
			file = sys.argv[3]
			ts = ssh_communication.SSHCommunication(target_full_id)
			ts.target_push(file)

		elif o in ("--pull"):
			target_full_id = sys.argv[2]
			ts = ssh_communication.SSHCommunication(target_full_id)
			ts.target_pull()

		elif o in ("--shutdown"):
			lm = libvirt_manage.LibvirtTerminate()

		else:
			print("Error")
			assert False, "unhandled option"

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
