#!/bin/bash

## debian ##
# libvirt = python3-guestfs, libvirt, python3-guestfs, libguestfs-tools
# apt = python3-apt
# cryptograpy = rustc, libssl-dev

## For debian, we need
apt install -y \
	rsync flex bison bc libelf-dev \
	python3 python3-pip \
	python3-guestfs python3-libvirt \
	python3-apt rustc libssl-dev \
	libvirt-daemon-system qemu-kvm libguestfs-tools

## We can then install the pip requirments
pip3 install \
	GitPython cryptography pyroute2.nftables
