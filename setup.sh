#!/bin/sh

## For debian, we need
apt install -y \
	rsync flex bison bc libelf-dev \
	python3 python3-pip \
	python3-guestfs python3-libvirt \
	python3-apt rustc libssl-dev \
	libvirt-daemon-system qemu-kvm libguestfs-tools virt-viewer

## We can then install the pip requirments
pip3 install \
	GitPython cryptography pyroute2.nftables paramiko requests

## And finally we run the python setup- Creates directories, etc.
python3 ./meros.py \
	--setup
