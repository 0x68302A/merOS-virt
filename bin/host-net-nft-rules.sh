#!/bin/sh

declare -x DEFAULT_GW=$(echo $(ip route | grep default) | cut -d " " -f 3)

sys_nftables_setup() {

	nft "add table FILTER"
	nft "add chain FILTER INPUT { type filter hook input priority 0; policy accept; }"
	nft "add rule FILTER INPUT ct state established,related accept;"
}

sys_nftables_net_access() {

	sysctl -q net.ipv4.ip_forward=1
	sysctl -q net.ipv6.conf.default.forwarding=0
	sysctl -q net.ipv6.conf.all.forwarding=0

	BR_ID=$1

	declare DEFAULT_GW=$(/sbin/ip route | awk '/default/ { print $3 }')

	nft "add table NAT"
	nft "add chain NAT PREROUTING { type nat hook prerouting priority -100; policy drop; }"
	nft "add rule NAT PREROUTING iif" $BR_ID "accept;"
	nft "add rule NAT PREROUTING iif" $BR_ID "tcp dport { 80, 443 } dnat $DEFAULT_GW;"

	nft "add chain NAT POSTROUTING { type nat hook postrouting priority 100 ; }"
	nft "add rule NAT POSTROUTING masquerade;"
}
