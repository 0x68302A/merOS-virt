#!/bin/sh

## For debian, we depend on:
apt install -y \
	rsync flex bison bc libelf-dev \
	python3 python3-pip \
	python3-guestfs python3-libvirt \
	rustc libssl-dev net-tools\
	libvirt-daemon-system qemu-kvm libguestfs-tools virt-viewer xpra

## TODO:
## Check for host distro, and configure as expected.

## Temp Debian bug fix
## https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=623536
mkdir -p /var/lib/libvirt/dnsmasq/
