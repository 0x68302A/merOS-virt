#!/bin/bash

set -uo pipefail

declare MOS_PATH=$(dirname "$(realpath $0)")
declare USER_ID=$(logname)
declare ARCH=$(uname -m)

declare DISTRO="debian"

source $MOS_PATH/bin/host-conf.sh
source $MOS_PATH/bin/host-net.sh
source $MOS_PATH/bin/host-net-nft-rules.sh
source $MOS_PATH/bin/qemu-extra.sh
source $MOS_PATH/bin/shutdown.sh

source $MOS_PATH/bin/kernel-build.sh
source $MOS_PATH/bin/chroot-build.sh
source $MOS_PATH/bin/bootstrap.sh
source $MOS_PATH/bin/vm-comm.sh

source_vm_var() {

	for f in $MOS_PATH/etc/conf/$DISTRO/$VM_ID/source/*
	do
		source $f
	done
}

root_check() {

	if [[ $(/usr/bin/id -u) -ne 0 ]]; then

		printf "Not running as root! \nFor more, use merOS -h \n"

	exit 0
	fi
}

case $1 in
-h|--help)

	sudo -u $USER_ID \
	view $MOS_PATH/etc/man
	exit 1
;;
--setup)

	root_check

	sys_apt_conf
	sys_grub_conf
	ln -sfn $MOS_PATH/meros.sh /usr/bin/meros

	exit 1
      ;;
--kernel-build)

	kernel_build

	exit 1
;;
--bootstrap)

	root_check
	bootstrap

	exit 1
;;
--build)

	root_check

	declare VM_ID=$2

	source_vm_var
	bootstrap
	build_vm

	exit 1
;;
--net-access)

	root_check

	declare BR_ID=$2.BR

	source_vm_var
	NFT_NAT_NET_ACCESS $BR_ID

	exit 1
;;
-i|--init)

	root_check

	declare VM_ID=$2

	source_vm_var

	init_master

	exit 1
;;
-c|--connect)

	declare VM_ID=$2

	source_vm_var
	ssh_connect

	exit 1
;;
-p|--push)

	declare FILE=$2
	declare VM_ID=$3

	ssh_push

	exit 1
;;
--pull)

	declare VM_ID=$2

	ssh_pull

	exit 1
	;;
--sync)

	declare VM_ID=$2

	ssh_sync

	exit 1
;;
--run)

	root_check

	declare IMAGE=$2
	declare BR_ID=$3
	declare MEM_MB=$4

	declare IMAGE_FILE=$(realpath $IMAGE)
	declare VM_ID=${IMAGE:0:3}
	declare VM_NIC=$VM_ID-$RANDOM

        nic_create $VM_NIC
	nic_attach $VM_NIC $BR_ID

	qemu_iso-qcow

	exit 1
;;
--brinit)

	root_check

	declare BR_ID=$2
	declare BR_IP=$RAND_IP

        nic_bridge_create $BR_ID $BR_IP
	dnsmasq_run $BR_ID

	exit 1
;;
--brkill)

	root_check

	declare BR_ID=$2

        ip link del $BR_ID && rm $MOS_PATH/etc/active/$BR_ID

	exit 1
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

	exit 1

;;
--clean)

	root_check

	rm -rf $MOS_PATH/etc/build/kernel/*
	rm -rf $MOS_PATH/etc/build/bootstrap/*

	exit 1
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
