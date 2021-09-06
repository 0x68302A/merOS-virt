#!/bin/bash

export default_gw=$(echo $(ip route | grep default) | cut -d " " -f 3)
export iface_nic="mersec_pub"

## Create Base for our firewall
nft "flush ruleset"
nft "add table FILTER"
nft "add chain FILTER INPUT { type filter hook input priority 0; policy accept; }"
nft "add rule FILTER INPUT ct state established,related accept;"

## Enable IPV4 forwarding
sysctl -q net.ipv4.ip_forward=1
sysctl -q net.ipv6.conf.default.forwarding=0
sysctl -q net.ipv6.conf.all.forwarding=0

## Grant net NAT access to our bridge interface
nft "add table NAT"
nft "add chain NAT PREROUTING { type nat hook prerouting priority -100; policy drop; }"
nft "add chain NAT POSTROUTING { type nat hook postrouting priority 100 ; }"

nft "add rule NAT PREROUTING iif" $iface_nic "accept;"
nft "add rule NAT PREROUTING iif" $iface_nic "tcp dport { 80, 443 } dnat " $default_gw ";"
nft "add rule NAT POSTROUTING masquerade;"
