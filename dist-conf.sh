#!/bin/sh

## For debian, we depend on:
apt install -y \
	rsync flex bison bc libelf-dev \
	python3 python3-pip \
	rustc libssl-dev net-tools\
	qemu-kvm

## TODO:
## Check for host distro, and configure as expected.

## Temp Debian bug fix
## https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=623536
mkdir -p /var/lib/libvirt/dnsmasq/
