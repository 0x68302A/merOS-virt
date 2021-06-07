#!/bin/sh

bootstrap() {

case $DISTRO in

debian)
	declare BOOTSTRAP_DIR=$MOS_PATH/etc/build/bootstrap/$DISTRO/BASE

	if [ -d $BOOTSTRAP_DIR ]
	then
		:
	else

	mkdir -p $BOOTSTRAP_DIR

	debootstrap \
		--variant=minbase \
		stable \
		$BOOTSTRAP_DIR/ \
		http://debian.a1.bg/debian/
	fi
	;;
alpine)
	declare BOOTSTRAP_DIR=$MOS_PATH/etc/build/bootstrap/$DISTRO/BASE

	MIRR='http://dl-cdn.alpinelinux.org/alpine'
	DNS1='1.1.1.1'
	DNS2='1.0.0.1'

	# Prepare (start)
	ARCH=`uname -m`
	mkdir -p $BOOTSTRAP_DIR
	cd $BOOTSTRAP_DIR

	# Download rootfs (start)
	FILE=`wget -qO- "$MIRR/latest-stable/releases/$ARCH/latest-releases.yaml" | grep -o -m 1 'alpine-minirootfs-.*.tar.gz'`
	wget "$MIRR/latest-stable/releases/$ARCH/$FILE" -O rootfs.tar.gz

	# Extract rootfs (start)
	tar -xf rootfs.tar.gz
	;;
esac
}
