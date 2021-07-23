#!/usr/bin/python3

import pyroute2
from pyroute2 import IPRoute

ifname = "anic_r"
brname = "br_r"

ip = IPRoute()

# dev = ip.link_lookup(ifname=ifname)[0]

def nic_create():
	ip.link("add",
		ifname=ifname,
		kind="tuntap",
		mode="tap")


def nic_create_bridge():
	ip.link("add",
		ifname=ifname,
		kind="bridge")




if __name__ == "__main__":
	nic_create()
