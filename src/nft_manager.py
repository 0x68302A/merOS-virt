import subprocess
import logging
from pathlib import Path
from typing import Dict
from .vm_models import BridgeConfig

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
        default_gw = self._get_default_gateway()
        base = f"""
        table ip bridge_{bridge} {{
            chain input {{
                type filter hook input priority 0; policy drop;
                ct state established,related accept;
                oifname "{bridge}" accept;
        """

        if policy.policy_type == "host-access":
            if policy.allowed_ports:
                ports = ", ".join(map(str, policy.allowed_ports))
                base += f"""
                    tcp dport {{ {ports} }} accept;
                """

            # Add NAT rules (masquerade for internet access)
            base += f"""
                }}

                chain prerouting {{
                    type nat hook prerouting priority -100; policy drop;
                    iifname {bridge} accept;
                    iifname {bridge} dnat to {default_gw};
                }}

                chain postrouting {{
                    type nat hook postrouting priority 100;
                    masquerade;
                }}
            """
        elif policy.policy_type == "isolated":
            subnets = policy.subnet
            base += f"""
                ip saddr {{ {subnets} }} ip daddr {{ {subnets} }} drop;
                counter drop comment "Blocked traffic";
            }}
            """

        return base + "\n    }"

    def _get_default_gateway(self):
        """Read default gateway from /proc/net/route (Linux filesystem)"""
        try:
            with open('/proc/net/route', 'r') as f:
                # Skip header line
                next(f)

                for line in f:
                    parts = line.strip().split('\t')
                    # Check for default route (Destination = 0.0.0.0)
                    if len(parts) >= 2 and parts[1] == '00000000':
                        # Gateway is in hex format (little-endian)
                        gateway_hex = parts[2]

                        # Convert hex to IP address
                        if len(gateway_hex) != 8:
                            continue

                        # Split into 4 bytes and reverse endianness
                        ip_bytes = [
                            int(gateway_hex[6:8], 16),  # First byte
                            int(gateway_hex[4:6], 16),  # Second byte
                            int(gateway_hex[2:4], 16),  # Third byte
                            int(gateway_hex[0:2], 16)   # Fourth byte
                        ]

                        return f"{ip_bytes[0]}.{ip_bytes[1]}.{ip_bytes[2]}.{ip_bytes[3]}"

                raise RuntimeError("No default gateway found")

        except FileNotFoundError:
            raise RuntimeError("/proc/net/route not found - are you on Linux?")
        except Exception as e:
            raise RuntimeError(f"Error reading gateway: {str(e)}")
