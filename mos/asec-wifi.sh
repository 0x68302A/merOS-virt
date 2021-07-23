#!/bin/bash


wifi_connect() {

IFACE=$2
NET_SSID=$3
NET_PASSWD=$4

killall wpa_supplicant
dhclient -r $IFACE
ifdown $IFACE
ip link set $IFACE down

case "$1" in
	"-scan")

	ip link set $IFACE up
	iwlist $IFACE scan | grep SSID
;;
	"-connect")

	wpa_passphrase "$NET_SSID" $NET_PASSWD | tee /etc/wpa_supplicant.conf
	wpa_supplicant -B -c /etc/wpa_supplicant.conf -i $IFACE && sleep 6
	dhclient -v $IFACE

	printf "Connected to $NET_SSID \n"
;;
esac
}
