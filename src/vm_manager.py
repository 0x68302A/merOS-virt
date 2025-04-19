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
        pid_file.unlink(missing_ok=True)

        if pid_file.exists():
            pid_file.unlink(missing_ok=True)
        
        try:
            # Prepare disks
            disk_info = {}
            for disk in config.disks:
                logger.debug(f"Preparing disk: {disk}")
                disk_data = self.disk_manager.create_disk(config.name, disk)
                # self.disk_manager.mount_disk(disk)
                disk_info[disk.label] = disk_data

            # Prepare networks
            network_info = {}
            for network in config.networks:
                logger.debug(f"Preparing network: {network}")
                self.network_manager.create_bridge(network.bridge, network.subnet)
            
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
                    "-netdev", f"bridge,id=net_{network.label},br={network.bridge}",
                    "-device", f"{network.model},netdev=net_{network.label}",
                ]

                self._save_state(config.name, {
                    "bridge": network.bridge,
                    "model": network.model 
                })

            # Add kernel Parameter for custom kernels
            if config.kernel:
                cmd += [
                    "-kernel", 
                    f"{config.kernel}"
                ]

                cmd += [
                    "-append", 
                    f"root=/dev/vda1"
                ]
             
 
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


            elapsed = time.time() - start_time
            logger.info(f"VM started successfully in {elapsed:.2f}s")
                
        except Exception as e:
            logger.error(f"Failed to start VM: {e}")
            raise

    def stop_vm(self, vm_name: str):
        pid = self._read_pid_file(vm_name)
        state = self._load_state(vm_name)
        try:
            self.network_manager.delete_bridge(state["network"]["bridge"])
        except Exception as e:
            logger.debug(f"Bridge is already deleted")
            pass

        if pid is None:
            raise RuntimeError(f"No running PID found for {vm_name}")
        try:
            os.kill(pid, signal.SIGTERM)
            self.remove_state(vm_name)
        except ProcessLookupError:
            pass  # Process already dead
        finally:
            self._get_pid_file(vm_name).unlink(missing_ok=True)

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
        
        # Get bridge from state file
        state_file = self.STATE_DIR / f"{vm_name}.json"
        try:
            with open(state_file) as f:
                state = json.load(f)
            bridge = state.get("network", {}).get("bridge")
        except (FileNotFoundError, json.JSONDecodeError):
            bridge = None
        
        # Verify bridge exists
        if bridge and self._is_bridge_active(bridge):
            return (True, bridge)
        return (True, None)  # Running but no bridge/bridge dead

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
            
    def _save_state(self, vm_name: str, network_config: dict):
        """Save network configuration to state file"""
        with open(self.STATE_DIR / f"{vm_name}.json", "w") as f:
            json.dump({"network": network_config}, f)  # Directly use the input dict

    def list_vms(self) -> list:
        """Return names of all VMs with state files"""
        return [f.stem for f in self.STATE_DIR.glob("*.json")]

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

    def _load_state(self, vm_name: str) -> Dict:
        state_path = self.STATE_DIR / f"{vm_name}.json"
        logger.debug(f"Loading state from {state_path}")
        with open(state_path) as f:
            return json.load(f)
    
    def remove_state(self, vm_name: str):
        state_path = self.STATE_DIR / f"{vm_name}.json"
        if state_path.exists():
            logger.debug(f"Removing state file {state_path}")
            state_path.unlink()
