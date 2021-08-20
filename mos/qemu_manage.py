#!/usr/bin/python3

import mos.helper as helper
import mos.networking as networking

import subprocess
import imp
import random as r


class QemuManage:
    def __init__(self, target_full_id):
        self.target_full_id = target_full_id
        h = helper.Helper()
        self.h = h
        self.mos_path  =  h.mos_path
        self.arch = h.arch
        
        self.mos_img_dir = self.h.mos_img_dir
        self.target_rootfs_img = self.mos_img_dir + "/" + self.target_full_id + ".img"
        self.mos_ssh_priv_key_dir = self.h.mos_ssh_priv_key_dir
        self.kernel_img = self.mos_img_dir + "/bzImage"


    def qemu_run(self):
        self.target_id_split = self.target_full_id.split("-")
        self.target_fam = self.target_id_split[0]
        self.target_id = self.target_id_split[1]
        
        self.conf_file = self.mos_path + "/conf/target/" + self.target_fam + "/qemu/" + self.target_id + ".qemu"
        imp.load_source("conf_file", self.conf_file)
        import conf_file
        
        cmd = self.qemu_default(self.target_id, self.target_rootfs_img, conf_file.target_ram_mb)
        subprocess.run(cmd, shell=True)


    def qemu_default(self, target_id, target_disk, target_ram_mb):
        default_qemu_args = [
                "qemu-system-" + self.h.arch,
                "-snapshot",
                "-daemonize",
                "-enable-kvm",
                "-m " + target_ram_mb,
                "-M pc",
                "-cpu host",
                "-smp cores=2",
                "--accel kvm,thread=multi",
                "-append 'root=/dev/sda1'",
                "-kernel " + self.kernel_img,
                "-display gtk",
                "-name " + target_id,
                "-drive file=" + target_disk + ",id=hd0",
                "-pidfile " + self.mos_path + "/data/proc/" + target_id + "-" + str(r.randint(0,100)) + ".pid"
            ]
            
        default_qemu_args  = " ".join(map(str,default_qemu_args))
        
        return default_qemu_args


    def netdev_attach(self,nic_id):
        self.nw = networking.Networking()
        self.rand_mac = self.nw.rand_mac_gen()
        
        device_network_args = [
                "-netdev tap",
                "ifname=" + nic_id,
                "script=no",
                "downscript=no",
                "id=" + nic_id,
                "-device e1000",
                "netdev=" + nic_id,
                "mac=" + self.rand_mac
            ]
        return device_network_args

