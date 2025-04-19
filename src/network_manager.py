import subprocess
import logging
from typing import Set

logger = logging.getLogger(__name__)

class NetworkManager:
    def __init__(self, verbose: bool = False):
        if verbose:
            logger.setLevel(logging.DEBUG)
    
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

            logger.debug(f"Bridge {bridge_name} activated")
        except subprocess.CalledProcessError as e:
            logger.error(f"Bridge creation failed: {e.stderr}")
            raise
    
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
