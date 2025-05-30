import subprocess
import json
import logging
import time
import guestfs

from pathlib import Path
from typing import Dict

from .app_config import AppConfig
from .vm_models import VirtualDisk

logger = logging.getLogger(__name__)

class DiskManager:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.disk_dir = Path(AppConfig.mos_disk_dir)
        self.disk_dir.mkdir(exist_ok=True)
        if self.verbose:
            logger.setLevel(logging.DEBUG)

    def create_disk(self, vm_name: str, disk: VirtualDisk) -> Dict:
        disk_path = self.disk_dir / f"{disk.label}"

        logger.info(f"Creating disk: {disk} for VM {vm_name}")

        if not disk_path.exists():
            start_time = time.time()
            logger.debug(f"Allocating {disk.size_gb}GB disk at {disk_path}")
            disk_size_kb = disk.size_gb*1024*1024*1024

            g = guestfs.GuestFS(python_return_dict=True)

            try:
                g.disk_create(str(disk_path), 'qcow2', disk_size_kb)
                logger.info(f"Successfully created QCOW2 image at {disk_path}")
            except Exception as e:
                logger.error(f"Error creating QCOW2 image: {e}")

                elapsed = time.time() - start_time
                logger.info(f"Disk created in {elapsed:.2f}s: {disk_path}")

        return {
            "path": disk_path
        }

    def clone_qcow2(self, src_qcow2_path, dest_qcow2_path, size_mb, rootfs_part):
        ## Resize disk
        ## TODO Handle resizing with guestfs
        ## part_list, truncate - Investigate
        create_cmd = ["qemu-img", "create", dest_qcow2_path, "-f", "qcow2" ,f"+{size_mb}M"]
        expand_cmd = ["virt-resize", "--expand", rootfs_part , src_qcow2_path, dest_qcow2_path]

        try:
            subprocess.run(create_cmd)
            subprocess.run(expand_cmd)
            logger.info(f"Sized {dest_qcow2_path}: {size_mb} MB")
        except Exception as e:
            logger.error(f"Failed to clone image: {e}")
