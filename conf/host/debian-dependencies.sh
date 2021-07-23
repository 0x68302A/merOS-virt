#!/bin/sh

APT_CONF() {

	APT_SYSTEM="iproute2 nftables"
	APT_QEMU="qemu qemu-utils"

	apt update && apt upgrade -y

	apt install -y $APT_SYSTEM $APT_QEMU

}
