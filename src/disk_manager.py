import subprocess
import json
import logging
import time
from pathlib import Path
from typing import Dict
from .vm_models import VirtualDisk

logger = logging.getLogger(__name__)

class DiskManager:
    MOUNT_ROOT = Path("current_mounts")
    DISK_ROOT = Path("data/images")

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.DISK_ROOT.mkdir(exist_ok=True)
        self.MOUNT_ROOT.mkdir(exist_ok=True)
        if self.verbose:
            logger.setLevel(logging.DEBUG)

    def create_disk(self, vm_name: str, disk: VirtualDisk) -> Dict:
        disk_path = self.DISK_ROOT / f"{disk.label}"
        disk.mount_point = self.MOUNT_ROOT / vm_name / disk.label

        logger.info(f"Creating disk: {disk} for VM {vm_name}")

        if not disk_path.exists():
            start_time = time.time()
            logger.debug(f"Allocating {disk.size_gb}GB disk at {disk_path}")

            dd_cmd = [
                "dd", "if=/dev/zero",
                f"of={disk_path}",
                "bs=1G",
                f"count={disk.size_gb}",
                "status=progress" if self.verbose else "status=none"
            ]

            try:
                process = subprocess.Popen(
                    dd_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                if self.verbose:
                    for line in process.stdout:
                        logger.debug(f"dd: {line.strip()}")

                process.wait()
                elapsed = time.time() - start_time
                logger.info(f"Disk created in {elapsed:.2f}s: {disk_path}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to create disk: {e}")
                raise

            logger.debug(f"Creating {disk.fs_type} filesystem on {disk_path}")
            mkfs_cmd = [
                "mkfs", f"-t{disk.fs_type}",
                "-L", disk.label,
                str(disk_path)
            ]

            try:
                subprocess.run(mkfs_cmd, check=True, capture_output=True)
                logger.debug("Filesystem created successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"Filesystem creation failed: {e.stderr}")
                raise

        return {
            "path": disk_path,
            "mount_point": disk.mount_point,
            "loop_device": self._attach_loop(disk_path)
        }

    def _attach_loop(self, disk_path: Path) -> str:
        logger.debug(f"Attaching loop device for {disk_path}")
        try:
            result = subprocess.run(
                ["losetup", "-f", "--show", str(disk_path)],
                capture_output=True,
                text=True,
                check=True
            )
            loop_dev = result.stdout.strip()
            logger.debug(f"Attached to {loop_dev}")
            return loop_dev
        except subprocess.CalledProcessError as e:
            logger.error(f"Loop device attachment failed: {e.stderr}")
            raise

    def mount_disk(self, disk: VirtualDisk):
        logger.info(f"Mounting disk to {disk.mount_point}")
        disk.mount_point.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ["mount", str(disk.mount_point)],
                check=True,
                capture_output=True
            )
            logger.debug("Mount successful")
        except subprocess.CalledProcessError as e:
            logger.error(f"Mount failed: {e.stderr}")
            raise

    def unmount_all(self, vm_name: str):
        mount_dir = self.MOUNT_ROOT / vm_name
        logger.info(f"Unmounting all disks for VM {vm_name}")

        for disk_dir in mount_dir.iterdir():
            logger.debug(f"Unmounting {disk_dir}")
            try:
                subprocess.run(
                    ["umount", str(disk_dir)],
                    check=True,
                    capture_output=True
                )
                loop_dev = f"/dev/loop{disk_dir.name}"
                subprocess.run(
                    ["losetup", "-d", loop_dev],
                    check=True,
                    capture_output=True
                )
                logger.debug(f"Released {loop_dev}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Cleanup warning: {e.stderr}")

        try:
            mount_dir.rmdir()
            logger.debug(f"Removed mount directory {mount_dir}")
        except OSError as e:
            logger.warning(f"Directory removal failed: {e}")
