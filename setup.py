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
	version = "0.6.2",
	author = "Aaran Ailbne",
	author_email = "mosp08@protonmail.com",

	description = ("merOS - Build && Interconnect a set of systems."),
	license = "GPLv3",
	keywords = "example documentation tutorial",
	url = "https://github.com/AranAilbhe/merOS-virt/",

	packages=['mos'],
	long_description=read('README'),

	classifiers=[
		"Development Status :: 3 - Alpha",
		"Topic :: Utilities",
		"License :: OSI Approved :: BSD License",
	],

	install_requires = [
				'GitPython',
				'cryptography',
				'pyroute2.nftables',
				'requests'
	],

	data_files = [("data/build", []),
					("data/build/bootstrap", []),
					("data/build/kernel", []),
					("data/images", []),
					("data/ssh_keys", []),
					("data/proc", []),
					("data/mos-shared", []),
					("conf/target", [])
	],

	scripts=["meros"]

)
