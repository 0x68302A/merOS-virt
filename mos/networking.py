#!/usr/bin/python3

import pyroute2
from pyroute2 import IPRoute
from pyroute2 import nftables

ip = IPRoute()

nft.chain('add',
		table='test0',
		name='test_chain0',
		hook='input',
		type='filter',
		policy=0)
