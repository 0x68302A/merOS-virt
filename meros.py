#!/usr/bin/python3


import mos.helper as helper
import mos.kernel_build as kernel_build
import mos.host_conf as host_conf
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
			hc.tree_conf()
			hc.syslink()
			sys.exit()

		elif o in ("--kernel-build"):
			kb = kernel_build.KernelBuild()
			kb.kernel_clone()
			kb.kernel_build()
			sys.exit()

		elif o in ("--build"):
			target_fam = sys.argv[2]
			tm = target_manage.TargetManage(target_fam)
			tm.main()
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
