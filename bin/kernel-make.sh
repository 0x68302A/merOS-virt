#!/bin/bash

kernel_build() {

	declare KERNEL_WORKDIR=$MOS_PATH/etc/build/kernel

	KERNEL_SOURCE_URL=http://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.19.105.tar.gz
	DOWNLOAD_URL=$(echo $KERNEL_SOURCE_URL| cut -f2 -d'=')
	ARCHIVE_FILE=${DOWNLOAD_URL##*/}

if [ ! -f $MOS_PATH/etc/build/kernel/linux-4.19.105.tar.xz ]; then
		wget -c $DOWNLOAD_URL -P $MOS_PATH/etc/build/kernel/
		cd $MOS_PATH/etc/build/kernel/ && tar -xvf $ARCHIVE_FILE -C $MOS_PATH/etc/build/kernel/
fi

	cd $MOS_PATH/etc/build/kernel/
	cd $(ls -d */)

	make mrproper
	make defconfig
	cp $MOS_PATH/etc/conf/kernel/kernel.config .
	make bzImage -j $(cat /proc/cpuinfo | grep processor | wc -l)
	make headers_install
	cp arch/$ARCH/boot/bzImage $MOS_PATH/etc/images/

}
