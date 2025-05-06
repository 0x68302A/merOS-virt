import subprocess
import logging
from typing import Set

logger = logging.getLogger(__name__)

class NetworkManager:
    def __init__(self, verbose: bool = False):
        if verbose:
            logger.setLevel(logging.DEBUG)

    @classmethod
    def create_tap(cls, tap_name: str, ip_addr: str, bridge_master: str):
        logger.info(f"Creating TAP device : {tap_name}")
        try:
            subprocess.run(
                ["sudo", "ip", "tuntap", "add", "name", tap_name, "mode", "tap"],
                check=True,
                capture_output=True
            )

            subprocess.run(
                ["sudo", "ip", "link", "set", tap_name, "master", bridge_master],
                check=True,
                capture_output=True
            )

            subprocess.run(
                ["sudo", "ip", "link", "set", tap_name, "up"],
                check=True,
                capture_output=True
            )

            logger.debug(f"TAP device {tap_name} configured")
        except subprocess.CalledProcessError as e:
            logger.error(f"TAP device status: {e.stderr}")
            pass

    @classmethod
    def create_bridge(cls, bridge_name: str, bridge_subnet: str):
        logger.info(f"Creating network bridge: {bridge_name}")
        try:
            subprocess.run(
                ["sudo", "ip", "link", "add", bridge_name, "type", "bridge"],
                check=True,
                capture_output=True
            )

            subprocess.run(
                ["sudo", "ip", "addr", "add", bridge_subnet, "dev", bridge_name],
                check=True,
                capture_output=True
            )

            subprocess.run(
                ["sudo", "ip", "link", "set", bridge_name, "up"],
                check=True,
                capture_output=True
            )

            subprocess.run(
                ["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"],
                check=True,
                capture_output=True
            )

            logger.debug(f"Bridge {bridge_name} configured")
        except subprocess.CalledProcessError as e:
            logger.error(f"Bridge status: {e.stderr}")
            pass

    @classmethod
    def delete_tap(cls, tap_name: str):
        logger.info(f"Deleting TAP device: {tap_name}")
        try:
            subprocess.run(
                ["sudo", "ip", "link", "del", tap_name],
                check=True,
                capture_output=True
            )

            logger.debug(f"TAP device {tap_name} removed")
        except subprocess.CalledProcessError as e:
            logger.error(f"TAP device status: {e.stderr}")
            pass

    @classmethod
    def delete_bridge(cls, bridge_name: str):
        logger.info(f"Removing network bridge: {bridge_name}")
        try:
            subprocess.run(
                ["sudo", "ip", "link", "del", bridge_name],
                check=True,
                capture_output=True
            )

            logger.debug(f"Bridge {bridge_name} removed")
        except subprocess.CalledProcessError as e:
            logger.error(f"Bridge removal failed: {e.stderr}")
            raise
