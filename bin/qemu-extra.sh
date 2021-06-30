#!/bin/bash

netdev_qemu() {

	export NIC_ID=$1

	printf "
	-netdev tap,ifname=$NIC_ID,script=no,downscript=no,id=$NIC_ID \
	-device e1000,netdev=$NIC_ID,mac=$(random_mac_gen) \
	"
}


qemu_iso-qcow() {

        sudo -u $USER_ID \
        qemu-system-x86_64 -snapshot -daemonize -enable-kvm -m $MEM_MB \
        -M pc -cpu host -smp cores=2 --accel kvm,thread=multi \
	-name $VM_ID \
        $(netdev_qemu $VM_NIC.NIC $(random_mac_gen)) \
        -drive file=$IMAGE_FILE \
        -pidfile $MOS_PATH/etc/active/$VM_ID-$RANDOM.PID
}

qemu_busybox() {

export STAGE=$MOS_PATH/etc/build/bootstrap/busybox
export BUILD=$MOS_PATH/etc/build/busybox
KERNEL_BZIMAGE=$MOS_PATH/etc/images/bzImage

qemu-system-x86_64 \
    -kernel $KERNEL_BZIMAGE \
    -initrd $BUILD/obj/initramfs.igz \
    -nographic -append "earlyprintk=serial,ttyS0 console=ttyS0"

}


