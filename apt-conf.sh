#!/bin/sh

## APT Configure
## For debian, we need

apt install -y \
	rsync flex bison bc libelf-dev \
	python3 python3-pip \
	python3-guestfs python3-libvirt \
	python3-apt rustc libssl-dev \
	libvirt-daemon-system qemu-kvm libguestfs-tools virt-viewer xpra
