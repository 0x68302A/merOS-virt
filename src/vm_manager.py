import subprocess
import logging
import time
import os
import signal

from pathlib import Path
from typing import Dict, Optional, Tuple

from .app_config import AppConfig
from .vm_models import VMConfig, Config
from .disk_manager import DiskManager
from .network_manager import NetworkManager
from .nft_manager import NFTManager

logger = logging.getLogger(__name__)

class VMManager:

    def __init__(self, config: Config, verbose: bool = False):
        self.state_dir = Path(AppConfig.mos_state_dir)
        self.config = config
        self.nft = NFTManager()
        self.disk_manager = DiskManager(verbose)
        self.network_manager = NetworkManager(verbose)
        self.state_dir.mkdir(exist_ok=True)

        if verbose:
            logger.setLevel(logging.DEBUG)

    def configure_bridge(self, bridge_name: str):
        if bridge_name not in self.config.bridges:
            logger.error(f"Bridge {bridge_name} not found in config")
            return

        bridge_config = self.config.bridges[bridge_name]
        logger.info(f"Configuring bridge: {bridge_name} ({bridge_config.subnet})")

        ## Configure bridge
        try:
            self.network_manager.create_bridge(bridge_name, bridge_config.subnet)
            logger.debug(f"Successfully configured {bridge_name}")
        except Exception as e:
            logger.error(f"Failed to configure {bridge_name}: {str(e)}")

        ## Configure associated nftables rules
        try:
            self.nft.create_bridge_rules(bridge_name, bridge_config)
            logger.debug(f"Successfully set netfilter rules for {bridge_name}")
        except Exception as e:
            logger.error(f"Failed to set netfilter rules for: {bridge_name}: {str(e)}")

    def start_vm(self, vm_name: str):
        vm = self.config.virtual_machines[vm_name]
        start_time = time.time()
        logger.info(f"Starting VM: {vm_name}")
        pid_file = self._get_pid_file(vm_name)

        try:
            ## Prepare disks
            disk_debug = {}
            for disk in vm.disks:
                logger.debug(f"Preparing disk: {disk.label}")
                disk_data = self.disk_manager.create_disk(vm.name, disk)
                disk_debug[disk.label] = disk_data

            for tap_interface in vm.networks:
                logger.debug(f"Preparing TAP Interface: {tap_interface.label}")
                self.network_manager.create_tap(tap_interface.label, tap_interface.ip_addr, tap_interface.bridge)

            ## Build QEMU command
            cmd = [
                f"qemu-system-{vm.arch}",
                "-name", vm.name,
                "-m", vm.memory,
                "-smp", str(vm.cpus),
                "-pidfile", str(pid_file),
                "-daemonize"
            ]

            ## Add disks
            for disk in vm.disks:
                cmd += [
                    "-drive",
                    f"file={disk_debug[disk.label]['path']},format={disk.fs_type},if=virtio"
                ]

            ## Add networks
            for network in vm.networks:
                cmd += [
                    "-netdev", f"tap,id=net_{network.label},ifname={network.label}",
                    "-device", f"{network.model},netdev=net_{network.label}",
                ]

            ## Handle KVM
            if vm.kvm == True:
                cmd += ["--enable-kvm"]

            ## Handle display
            if vm.display == False:
                cmd += ["-display", "none"]

            ## Add kernel Parameter for custom kernels
            if vm.kernel:
                cmd += ["-kernel", f"{AppConfig.mos_path}/{vm.kernel}"]
                cmd += ["-append", f"root=/dev/vda1"]

            ## Add extra arguments
            extra_args = []

            for arg in vm.extra_args:
                # Split if the argument contains spaces but doesn't start with a quote
                if " " in arg and not (arg.startswith('"') or arg.startswith("'")):
                    extra_args.extend(arg.split())
                else:
                    extra_args.append(arg)

            cmd.extend(extra_args)

            logger.debug(f"QEMU command: {' '.join(cmd)}")

            ## Start VM
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            time.sleep(0.5)
            elapsed = time.time() - start_time

            if process.returncode != 0:
                logger.error(f"VM failed to start after {elapsed:.2f}s. Error:\n{stderr.strip()}")
            else:
                logger.debug(f"VM started successfully in {elapsed:.2f}s")
                if stderr.strip():
                    logger.debug(f"Qemu started with warnings:\n{stderr.strip()}")
                if stdout.strip():
                    logger.debug(f"Qemu output:\n{stdout.strip()}")

        except Exception as e:
            logger.error(f"Failed to start VM: {e}")
            raise

    def delete_bridge(self, bridge_name: str):
        if bridge_name not in self.config.bridges:
            logger.error(f"Bridge {bridge_name} not found in config")
            return

        bridge_config = self.config.bridges[bridge_name]
        logger.info(f"Configuring bridge: {bridge_name} ({bridge_config.subnet})")

        ## Deconfigure bridge
        try:
            self.network_manager.delete_bridge(bridge_name)

        except Exception as e:
            logger.error(f"Failed to configure {bridge_name}: {str(e)}")

        # Deconfigure assoaciated nftables rules
        try:

            self.nft.remove_bridge_rules(bridge_name)
            logger.debug(f"Successfully deleted {bridge_name}")
        except Exception as e:
            logger.error(f"Failed to delete nft rules for: {bridge_name}: {str(e)}")

    def stop_vm(self, vm_name: str):
        vm = self.config.virtual_machines[vm_name]
        pid = self._read_pid_file(vm.name)
        start_time = time.time()
        logger.info(f"Starting VM: {vm_name}")
        pid_file = self._get_pid_file(vm_name)

        ## Delete TAP interfaces
        network_debug = {}
        try:
            for network in vm.networks:
                logger.debug(f"Deleting {vm.name} TAPs")
                self.network_manager.delete_tap(network.label)
        except Exception as e:
            logger.debug(f"TAP interface is already deleted")
            pass

        ## Stop related qemu proccess
        try:
            os.kill(pid, signal.SIGTERM)
        except:
            pass  # Process already dead

    def _get_status(self, vm_name: str) -> Tuple[bool, Optional[str]]:
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
            is_running = self._get_status(vm_name)
            statuses[vm_name] = {
                "running": is_running,
            }
        return statuses


    def list_vms(self) -> list:
        """Return names of all VMs with state files"""
        return [f.stem for f in self.state_dir.glob("*.pid")]

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
        return self.state_dir / f"{vm_name}.pid"

    def _read_pid_file(self, vm_name: str) -> Optional[int]:
        pid_file = self._get_pid_file(vm_name)
        try:
            return int(pid_file.read_text().strip())
        except (FileNotFoundError, ValueError):
            return None

    def _cleanup_networks(self, config: VMConfig):
        """Rollback network rules on failure"""
        for net in config.networks:
            self.nft.remove_bridge_rules(bridge.name)
