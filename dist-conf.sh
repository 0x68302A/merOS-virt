#!/bin/sh

## Must be run with uid 0
## Load OS information
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS="$ID"
else
    echo "Cannot determine OS. /etc/os-release not found."
    exit 1
fi

case "$OS" in
    debian|ubuntu)
        echo "Detected Debian-based system: $OS"
		apt install -y \
			rsync flex bison bc libelf-dev \
			python3 python3-pip python3-guestfs \
			guestfs-tools \
			rustc libssl-dev net-tools \
			qemu-kvm &&
		mkdir -p /var/lib/libvirt/dnsmasq/
		## https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=623536
        ;;
    alpine|postmarketos)
        echo "Detected Alpine Linux"
		apk update &&
		apk add \
			rsync \
			python3 py3-pip \
			libguestfs-dev guestfs-tools \
			open-vm-tools &&
        mkdir -p usr/lib/guestfs
        ;;
    centos|rhel|fedora)
        echo "Detected Red Hat-based system: $OS"
        echo "Unsupported OS: $OS"
        ;;
    *)
        echo "Unsupported or unknown OS: $OS"
        # Default or fallback commands
        ;;
esac
