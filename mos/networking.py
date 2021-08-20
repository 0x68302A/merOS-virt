#!/usr/bin/python3

import mos.helper as helper

from pathlib import Path
import pyroute2
from pyroute2 import IPRoute
from pyroute2 import nftables

class Networking:
    def __init__(self):
        self.ipr = IPRoute()
        self.h = helper.Helper()

    def rand_ip_gen(self):
        rand_255_01 = random.randint(0, 255)
        rand_255_02 = random.randint(0, 255)
        rand_full_ip = "10.0." + rand_255_01 + "." + rand_255_02

        return rand_full_ip

    def rand_mac_gen(self):
        rand_mac_string = "52:54:00:%02x:%02x:%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            )
        return rand_mac_string


    def bridge_create(self, br_id, br_ip):
        br_id = br_id + ".BR"
        ipr.link('add', ifname=br_id, kind='bridge')
        ipr.addr('add', index=dev,
                address='10.0.0.1', mask=24,
                broadcast='10.0.0.255')

        Path(self.h.mos_path + "/conf/proc/" + br_id).touch()




''''
        def nftables(json_conf):


ip = IPRoute()

nft.chain('add',
		table='test0',
		name='test_chain0',
		hook='input',
		type='filter',
		policy=0)
'''