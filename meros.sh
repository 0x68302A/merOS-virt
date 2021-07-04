#!/bin/bash

set -uo pipefail

declare MOS_PATH=$(dirname "$(realpath $0)")
declare USER_ID=$(logname)
declare ARCH=$(uname -m)

declare DISTRO="debian"

for f in $MOS_PATH/bin/*; do source $f; done

source_vm_var() {

	for f in $MOS_PATH/etc/conf/$DISTRO/$VM_ID/source/*; do source $f; done

}

root_check() {

	if [[ $(/usr/bin/id -u) -ne 0 ]]
	then printf "Not running as root! \nFor more, use merOS -h \n"

	exit 0
	fi
}

case $1 in
-h|--help)

	sudo -u $USER_ID \
	view $MOS_PATH/etc/man
	exit 0
;;
--setup)

	root_check

	sys_apt_conf
	sys_grub_conf
	ln -sfn $MOS_PATH/meros.sh /usr/bin/meros

	exit 0
      ;;
--kernel-build)

	kernel_build

	exit 0
;;
--bootstrap)

	root_check
	bootstrap

	exit 0
;;
--build)

	root_check

	declare VM_ID=$2

	source_vm_var
	bootstrap
	build_vm

	exit 0
;;
--build-busybox)

#	bootstrap_busybox
	build_busybox

	exit 0
;;
--net-access)

	root_check

	declare BR_ID=$2.BR

	sys_nftables_net_access $BR_ID

	exit 0
;;
-i|--init)

	root_check

	declare VM_ID=$2

	source_vm_var

	init_master

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
--run-busybox)
	qemu_busybox
;;
--run)

	root_check

	declare IMAGE=$2
	declare BR_ID=$3
	declare MEM_MB="${4:-1024}"

	declare IMAGE_FILE=$(realpath $IMAGE)
	declare VM_ID=${IMAGE:0:4}
	declare VM_NIC=$VM_ID-$RANDOM

        nic_create $VM_NIC
	nic_attach $VM_NIC $BR_ID

	qemu_iso-qcow

	exit 0
;;
--brinit)

	root_check

	export BR_ID=$2
#	declare BR_IP=$RAND_IP

        nic_bridge_create $BR_ID $RAND_IP
	dnsmasq_run

	exit 0
;;
--brkill)

	root_check

	declare BR_ID=$2

        ip link del $BR_ID && rm $MOS_PATH/etc/active/$BR_ID

	exit 0
;;
--shutdown)

	root_check

	declare -x VM_ID=$2

	if [ $VM_ID = "all" ]
	then
		kill_all
	else
		kill
	fi

	exit 0

;;
--clean)

	root_check

	rm -rf $MOS_PATH/etc/build/kernel/*
	rm -rf $MOS_PATH/etc/build/bootstrap/*

	exit 0
;;
-V|--verbose)
    declare verbose=1
    set -xv  # Set xtrace and verbose mode.
    ;;
*)
	printf "merOS command not found-\nEnter meros -h for help \n"
;;
--)
    shift
    break
;;
esac
shift
