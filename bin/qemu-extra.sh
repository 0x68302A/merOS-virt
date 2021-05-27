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
        -M  pc -cpu SandyBridge,enforce -smp 2 \
        $(netdev_qemu $VM_NIC.NIC $(random_mac_gen)) \
        -drive file=$IMAGE_FILE \
        -pidfile $MOS_PATH/etc/active/$VM_ID-$RANDOM.PID
}
