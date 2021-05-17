#!/bin/bash

sys_apt_conf() {

	APT_SYSTEM="iproute2 nftables"
	APT_QEMU="qemu qemu-utils"

	apt update && apt upgrade -y

	apt install -y $APT_SYSTEM $APT_QEMU

}

sys_grub_conf() {

	cp $MOS_PATH/etc/host/grub /etc/default/grub
	update-grub

}
