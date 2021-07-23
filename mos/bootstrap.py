#!/usb/bin/python3

import mos
from mos import *

import os
import requests
import re
import sys
import string
import tarfile

bootstrapDir = mos.mosPath + "/etc/build/bootstrap/" + mos.targetDistro
bootstrapBase = mos.mosPath + bootstrapDir + "/base"
uname = os.uname()
arch = str(uname[4])

mirror = "http://dl-cdn.alpinelinux.org/alpine/"
mirrorRelease = mirror + "latest-stable/releases/" + arch + "/latest-releases.yaml"
mirrorReleases = mirror + "latest-stable/releases/" + arch + "/"


def bootstrap():

  DNS1 = "1.1.1.1"
  DNS2 = "1.0.0.1"

  if not os.path.isdir(bootstrapDir):
    os.makedirs(bootstrapDir)
  else:
    None

  os.chdir(bootstrapDir)

  latestReleases = requests.get(mirrorRelease, allow_redirects=True)
  open("latest-releases.yaml", 'wb').write(latestReleases.content)

  with open("latest-releases.yaml", "r") as file:
    for line in file:
     if re.search("file: alpine-minirootfs-.*.tar.gz", line):
        rootfsIDFull = str(line)
        rootfsIDSplit = rootfsIDFull.split()

        rootfsID = rootfsIDSplit[1]

  rootfsLink = mirrorReleases + rootfsID

  rootfsFile = requests.get(rootfsLink, allow_redirects=True)
  open("rootfs.tar.gz", 'wb').write(rootfsFile.content)

'''
  tarFile = tarfile.open("rootfs.tar.gz")
  tarFile.extractall(".")
  tarFile.close
'''
