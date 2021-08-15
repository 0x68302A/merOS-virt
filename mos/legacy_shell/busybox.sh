#!/bin/bash

export STAGE=$MOS_PATH/etc/build/bootstrap/
export BUILD=$MOS_PATH/etc/build/busybox
# export TOP=$STAGE/teeny-linux
export BB_URL="https://busybox.net/downloads/busybox-1.26.2.tar.bz2"
bootstrap_busybox() {

	mkdir -p $STAGE

	cd $STAGE
	git clone https://git.busybox.net/busybox --depth 1

	cd $STAGE/busybox
	mkdir -pv $BUILD/obj/busybox-x86

	make O=$BUILD/obj/busybox-x86 defconfig
	make O=$BUILD/obj/busybox-x86 menuconfig

	## Build BusyBox as a static binary (no shared libs)

	cd $BUILD/obj/busybox-x86
	make -j2
	make install

	mkdir -pv $BUILD/initramfs/x86-busybox
	cd $BUILD/initramfs/x86-busybox
	mkdir -pv {bin,dev,sbin,etc,proc,sys/kernel/debug,usr/{bin,sbin},lib,lib64,mnt/root,root}
	cp -av $BUILD/obj/busybox-x86/_install/* $BUILD/initramfs/x86-busybox
	sudo cp -av /dev/{null,console,tty,sda1} $BUILD/initramfs/x86-busybox/dev/

	# vi $BUILD/initramfs/x86-busybox/init

cat <<EOF >> $BUILD/initramfs/x86-busybox/init
#!/bin/sh

mount -t proc none /proc
mount -t sysfs none /sys
mount -t debugfs none /sys/kernel/debug

echo -e "\nBoot took $(cut -d' ' -f1 /proc/uptime) seconds\n"

exec /bin/sh
EOF

	chmod +x $BUILD/initramfs/x86-busybox/init

}

build_busybox() {

	cd $BUILD/initramfs/x86-busybox
	find . | cpio -H newc -o > ../initramfs.cpio
	cd ../

	cat initramfs.cpio | gzip > $BUILD/obj/initramfs.igz

}

