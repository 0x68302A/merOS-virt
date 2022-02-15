#!/usr/bin/python3

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name = "merOS-virt",
	version = "0.8.6",
	author = "Aaran Ailbne",
	author_email = "mosp08@protonmail.com",

	description = ("merOS - Build && Interconnect a set of systems."),
	license = "GPLv3",
	keywords = "meros-virt isolation security",
	url = "https://github.com/AranAilbhe/merOS-virt/",

	packages=['mos'],
	long_description=read('README.md'),

	classifiers=[
		"Development Status :: 3 - Alpha",
		"Topic :: Utilities",
		"License :: GPLv3 License",
	],

	install_requires = [
				'GitPython',
				'cryptography',
				'pyroute2.nftables',
				'requests'
	],

	scripts=["meros"]
)

## Build expected file structure

def tree_conf():

	os.makedirs("data/build", mode = 0o777, exist_ok = True)
	os.makedirs("data/build/kernel", mode = 0o777, exist_ok = True)
	os.makedirs("data/build/bootstrap", mode = 0o777, exist_ok = True)
	os.makedirs("data/images", mode = 0o777, exist_ok = True)
	os.makedirs("data/ssh_keys", mode = 0o777, exist_ok = True)
	os.makedirs("data/mos-shared", mode = 0o777, exist_ok = True)
	os.makedirs("conf/target", mode = 0o777, exist_ok = True)

tree_conf()
