#!/bin/sh

declare -x N1=$(( $RANDOM % 155 + 1 ))
declare -x N2=$(( $RANDOM % 155 + 1 ))
declare -x RAND_IP="10.0.$N1.$N2"


random_mac_gen() {

hexdump -n 6 -ve '1/1 "%.2x "' /dev/random |\
awk -v a="2,6,a,e" -v r="$RANDOM" '
    BEGIN {
        srand(r);
    }
    NR==1 {
        split(a, b, ",");
        r=int(rand() * 4 + 1);
        printf("%s%s:%s:%s:%s:%s:%s\n", substr($1, 0, 1), b[r], $2, $3, $4, $5, $6);
    }
'

}

nic_bridge_create() {

	declare BR_ID=$1.BR
	declare BR_IP=$2

	ip link add name $BR_ID type bridge
	ip addr add $BR_IP/24 dev $BR_ID
	ip link set $BR_ID up

	touch $MOS_PATH/etc/active/$BR_ID
}

nic_create() {

	modprobe tun
	declare NIC_ID=$1.NIC

	ip tuntap add dev $NIC_ID mode tap user $USER_ID
	ip link set $NIC_ID up promisc on

	touch $MOS_PATH/etc/active/$NIC_ID
}

nic_attach() {

        ip link set $1.NIC master $2.BR
}

dnsmasq_run() {

	IFACE_ID=$1

	START_IP=10.0.$N1.$(($N2+1))
	END_IP=10.0.$N1.$(($N2+100))

	dnsmasq --interface=$IFACE_ID --conf-file=/dev/null \
	--except-interface=lo --bind-dynamic \
	--dhcp-range=$START_IP,$END_IP --pid-file=$ACTIVE_DIR/$IFACE_ID.DNSMASQ.PID

}
