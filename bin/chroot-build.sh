#!/bin/bash

chroot_configure() {


	export CHROOT_DIR=$MOS_PATH/etc/build/bootstrap/$DISTRO/$VM_ID
	declare -x CONF_DIR=$MOS_PATH/etc/conf/$DISTRO
	declare -x CHROOT_CONF_DIR=$CONF_DIR/$VM_ID/includes.chroot

	rm -rf $CHROOT_DIR/etc/ssh/ssh_host_rsa_key
	rm -rf $MOS_PATH/etc/ssh-keys/$VM_ID-id_rsa

	cp -rn $MOS_PATH/etc/build/bootstrap/$DISTRO/BASE/* $CHROOT_DIR/

	sudo -u $USER_ID \
	ssh-keygen -f "/home/$USER_ID/.ssh/known_hosts" -R "[10.0.4.4]:2022"

	cp -r $CHROOT_CONF_DIR/* $CHROOT_DIR/

	ssh-keygen -t rsa -N "" -f \
	$CHROOT_DIR/etc/ssh/ssh_host_rsa_key

	sudo -u $USER_ID \
	ssh-keygen -t rsa -N "" -f \
	$MOS_PATH/etc/ssh-keys/$VM_ID-id_rsa

	mkdir -p $CHROOT_DIR/etc/ssh/
	cat $MOS_PATH/etc/ssh-keys/$VM_ID-id_rsa.pub \
	> $CHROOT_DIR/etc/ssh/authorized_keys

	# touch $CHROOT_DIR/etc/resolv.conf
	echo "nameserver $(/sbin/ip route | awk '/default/ { print $3 }') \n nameserver ${MACH_VAR[NS]}" > $CHROOT_DIR/etc/resolv.conf

	chroot $CHROOT_DIR /root/0100-conf.chroot
	chroot $CHROOT_DIR /root/0150-packages.chroot



}

qemu_qcow_build() {

	declare ROOT_QCOW=$MOS_PATH/etc/images/$VM_ID-$DISTRO-sda.qcow2
	rm -rf $ROOT_QCOW

	virt-make-fs \
		--format qcow2 \
		--type ext4 \
		--size +${MACH_VAR[EXTRA_SIZE]} \
		$CHROOT_DIR \
		$ROOT_QCOW \
	  ;
		sudo chmod 0666 $ROOT_QCOW

	echo "--5/5 # Built image "
}
