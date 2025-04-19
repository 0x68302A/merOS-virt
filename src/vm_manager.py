import subprocess
import json
import logging
import time
import os
import signal
from pathlib import Path
from typing import Dict, Optional, Tuple
from .vm_models import VMConfig
from .disk_manager import DiskManager
from .network_manager import NetworkManager

logger = logging.getLogger(__name__)

class VMManager:
    STATE_DIR = Path("state")
    
    def __init__(self, verbose: bool = False):
        self.disk_manager = DiskManager(verbose)
        self.network_manager = NetworkManager(verbose)
        self.STATE_DIR.mkdir(exist_ok=True)
        if verbose:
            logger.setLevel(logging.DEBUG)
    
    def start_vm(self, config: VMConfig):
        start_time = time.time()
        logger.info(f"Starting VM: {config.name}")
        pid_file = self._get_pid_file(config.name)
        
        try:
            # Prepare disks
            disk_info = {}
            for disk in config.disks:
                logger.debug(f"Preparing disk: {disk}")
                disk_data = self.disk_manager.create_disk(config.name, disk)
                # self.disk_manager.mount_disk(disk)
                disk_info[disk.label] = disk_data

            # Prepare networks Bridges 
            network_info = {}
            for network in config.networks:
                logger.debug(f"Preparing network: {network}")
                self.network_manager.create_bridge(network.bridge, network.subnet)
                self.network_manager.create_tap(network.label, network.subnet, network.bridge)
            
            # Build QEMU command
            cmd = [
                "qemu-system-x86_64",
                "-name", config.name,
                "-m", config.memory,
                "-smp", str(config.cpus),
                "-daemonize",
                "-pidfile", str(pid_file)
            ]

            # Add disks
            for disk in config.disks:
                cmd += [
                    "-drive", 
                    f"file={disk_info[disk.label]['path']},format={disk.fs_type},if=virtio"
                ]

            # Add networks
            for network in config.networks:
                cmd += [
                    "-netdev", f"tap,id=net_{network.label},ifname={network.label}",
                    "-device", f"{network.model},netdev=net_{network.label}",
                ]

            # Add kernel Parameter for custom kernels
            if config.kernel:
                cmd += ["-kernel", f"{config.kernel}"]
                cmd += ["-append", f"root=/dev/vda1"]
             
            # Add extra arguments
            cmd.extend(config.extra_args)
            
            logger.debug(f"QEMU command: {' '.join(cmd)}")
            
            # Start VM
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(0.5)

            elapsed = time.time() - start_time
            logger.info(f"VM started successfully in {elapsed:.2f}s")
                
        except Exception as e:
            logger.error(f"Failed to start VM: {e}")
            raise

    def stop_vm(self, config: VMConfig):
        pid = self._read_pid_file(config.name)
        network_info = {}

        try:
            for network in config.networks:
                logger.debug(f"Deleting {network} TAPs")
                self.network_manager.delete_tap(network.label)
        except Exception as e:
            logger.debug(f"Bridge is already deleted")
            pass

        try:
            for network in config.networks:
                logger.debug(f"Deleting {network} bridges")
                self.network_manager.delete_bridge(network.bridge)
        except Exception as e:
            logger.debug(f"TAP is already deleted")
            pass

        try:
            os.kill(pid, signal.SIGTERM)
        except:
            pass  # Process already dead

    def get_status(self, vm_name: str) -> Tuple[bool, Optional[str]]:
        """
        Returns: 
            Tuple of (is_running: bool, bridge: Optional[str])
        """
        # Check PID status first
        pid = self._read_pid_file(vm_name)
        if pid is None:
            return (False, None)
        
        try:
            os.kill(pid, 0)  # Check if process exists
        except ProcessLookupError:
            self._get_pid_file(vm_name).unlink(missing_ok=True)
            return (False, None)
        
    def _is_bridge_active(self, bridge_name: str) -> bool:
        """Check if bridge interface exists and is up"""
        try:
            result = subprocess.run(
                ["ip", "link", "show", bridge_name],
                capture_output=True,
                text=True
            )
            return "UP" in result.stdout
        except subprocess.CalledProcessError:
            return False

    def get_all_statuses(self) -> Dict[str, Dict[str, str]]:
        """Returns detailed status for all VMs"""
        statuses = {}
        for vm_name in self.list_vms():
            is_running, bridge = self.get_status(vm_name)
            statuses[vm_name] = {
                "running": is_running,
                "bridge": bridge if bridge else "N/A"
            }
        return statuses
            

    def list_vms(self) -> list:
        """Return names of all VMs with state files"""
        return [f.stem for f in self.STATE_DIR.glob("*.pid")]

    def is_running(self, vm_name: str) -> bool:
        pid = self._read_pid_file(vm_name)
        if pid is None:
            return False
        try:
            os.kill(pid, 0)  # Check if process exists
            return True
        except ProcessLookupError:
            self._get_pid_file(vm_name).unlink(missing_ok=True)
            return False

    def _get_pid_file(self, vm_name: str) -> Path:
        return self.STATE_DIR / f"{vm_name}.pid"
    
    def _read_pid_file(self, vm_name: str) -> Optional[int]:
        pid_file = self._get_pid_file(vm_name)
        try:
            return int(pid_file.read_text().strip())
        except (FileNotFoundError, ValueError):
            return None
