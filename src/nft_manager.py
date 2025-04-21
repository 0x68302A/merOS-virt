import subprocess
import logging
from pathlib import Path
from typing import Dict
from .vm_models import BridgeConfig # Your existing model

class NFTManager:
    def _exec_nft(self, command: str):
        try:
            subprocess.run(
                ["sudo", "nft", "-f", "-"],
                input=command,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logging.error(f"NFT command failed: {e.stderr}")
            raise

    def create_bridge_rules(self, bridge: str, policy: BridgeConfig):
        """Idempotent rule creation with reference counting"""
        rules = self._generate_rules(bridge, policy)
        self._exec_nft(rules)
        logging.info(f"Created rules for {bridge} ({policy.policy_type})")

    def remove_bridge_rules(self, bridge: str):
        """Safe rule removal with reference counting"""
        logging.debug(f"Bridge {bridge} still in use")

        self._exec_nft(f"delete table ip bridge_{bridge}")
        logging.info(f"Removed rules for {bridge}")

    def _generate_rules(self, bridge: str, policy: BridgeConfig) -> str:
        base = f"""
        table ip bridge_{bridge} {{
            chain input {{
                type filter hook input priority filter; policy drop;
                iifname "{bridge}" accept
                oifname "{bridge}" accept
        """
        
        if policy.policy_type == "host-access":
            if policy.allowed_ports:
                ports = ", ".join(map(str, policy.allowed_ports))
                base += f"""
                    ct state established,related accept
                    tcp dport {{ {ports} }} accept
                    meta nftrace set 1  # Enable tracing
                """
        if policy.policy_type == "isolated":
            subnets = policy.subnet
            base += f"""
                ip saddr {{ {subnets} }} ip daddr {{ {subnets} }} accept
                counter drop comment "Blocked traffic"
            """
            
        return base + "\n            }\n        }"
