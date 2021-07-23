#!/usr/bin/python3

import os
import sys
import mos
from mos import *

from shutil import *
import distutils
from distutils import *
from distutils import dir_util
import subprocess
from os import chmod
from Crypto.PublicKey import RSA

imgDir = mos.mosPath + "/etc/images"
confDir = mos.mosPath + "/etc/conf/" + targetDistro + "/" + mos.vmID + "/includes.chroot"
chrootDir = mos.mosPath + "/etc/build/bootstrap/" + targetDistro + "/" + mos.vmID
chrootConfDir = chrootDir + mos.vmID + "/includes.chroot"

userSSHKeysDir =  "/home/" + os.getlogin() + "/" + "./ssh/"
mosSSHKeysDir = mos.mosPath + "/etc/ssh-keys"

targetSSHDir = chrootDir + "/etc/ssh"

def chroot_build():
	if not os.path.exists(chrootDir):
		os.makedirs(chrootDir)
		os.chdir(mos.bootstrapDir)

		tarFile = tarfile.open("rootfs.tar.gz")
		tarFile.extractall(mos.vmID)
		tarFile.close

		distutils.dir_util.copy_tree(confDir, chrootDir)
	else:
		None


def gen_keys():
	key = RSA.generate(2048)

	if not os.path.exists(targetSSHDir):
		os.makedirs(targetSSHDir)
	else:
		None

	## Write Target host key
	with open(targetSSHDir + "/ssh_host_rsa_key", 'wb') as content_file:
		chmod(targetSSHDir + "/ssh_host_rsa_key", 0o0600)
		content_file.write(key.exportKey('PEM'))

	## Write mos authentication pair
	with open(mosSSHKeysDir + "/" + mos.vmID + "-id_rsa", 'wb') as content_file:
		chmod(mosSSHKeysDir + "/" + mos.vmID + "-id_rsa", 0o0600)
		content_file.write(key.exportKey('PEM'))
		pubkey = key.publickey()
	with open(targetSSHDir + "/authorized_keys", 'wb') as content_file:
		content_file.write(pubkey.exportKey('OpenSSH'))
def chroot_configure():
	os.chroot(chrootDir)
	with open("/etc/resolv.conf", 'w') as file:
		file.write("nameserver " + defaultGw + "\n")

	subprocess.run("/root/0100-conf.chroot", shell=True)
	subprocess.run("/root/0150-packages.chroot", shell=True)

'''
ssh-keygen -f "/home/$USER_ID/.ssh/known_hosts" -R "[10.0.4.4]:2022" TODO
'''
