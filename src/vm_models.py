import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)

@dataclass
class VirtualDisk:
    label: str
    size_gb: int = 2
    fs_type: str = "ext4"
    mount_point: Optional[Path] = None

    def __str__(self):
        return f"Disk(label={self.label}, size={self.size_gb}GB, fs={self.fs_type})"

@dataclass
class BridgePolicy:
    name: str
    policy_type: str = "host-access"  # Modified with default value
    allowed_ports: Optional[List[int]] = None
    allowed_subnets: Optional[List[str]] = None
    allow_icmp: bool = False

@dataclass
class NetworkInterface:
    label: str
    bridge: str = "br0"
    subnet: str = "10.10.10.255"
    model: str = "virtio"
    ip_addr: str = None
    mac: Optional[str] = None
    policy: BridgePolicy = field(default_factory=BridgePolicy)  # New field

    def __str__(self):
        return (f"Network(label={self.label}, bridge={self.bridge}, "
                f"policy={self.policy.policy_type}, model={self.model})")

@dataclass
class VMConfig:
    name: str
    memory: str = "2G"
    kernel: str = None
    cpus: int = 2
    disks: List[VirtualDisk] = field(default_factory=list)
    networks: List[NetworkInterface] = field(default_factory=list)
    template: str = "default"
    extra_args: List[str] = field(default_factory=list)

    def __str__(self):
        return (f"VM(name={self.name}, memory={self.memory}, cpus={self.cpus}, "
                f"networks={[n.policy.policy_type for n in self.networks]})")

class VMConfigLoader:
    @staticmethod
    def load_config(path: Path) -> Dict[str, VMConfig]:
        logger.info(f"Loading VM configuration from {path}")
        with open(path) as f:
            data = yaml.safe_load(f)
        
        templates = data.get('templates', {})
        bridge_policies = data.get('bridges', {})  # New: Load bridge policies
        
        vms = {}
        for vm_name, vm_data in data['virtual_machines'].items():
            template = templates.get(vm_data.get('template', 'default'), {})
            
            networks = []
            for network in vm_data.get('networks', []):
                # Merge bridge policy with network config
                policy_data = bridge_policies.get(network.get('bridge'), {})
                networks.append(NetworkInterface(
                    **network,
                    policy=BridgePolicy(
                        name=network.get('bridge', 'br0'),
                        **policy_data
                    )
                ))
            
            vms[vm_name] = VMConfig(
                name=vm_name,
                memory=vm_data.get('memory', template.get('memory', "2G")),
                cpus=vm_data.get('cpus', template.get('cpus', 2)),
                kernel=vm_data.get('kernel', template.get('kernel', None)),
                disks=[VirtualDisk(**d) for d in vm_data.get('disks', [])],
                networks=networks,
                extra_args=vm_data.get('extra_args', [])
            )
        
        logger.info(f"Loaded {len(vms)} VMs with bridge policies")
        return vms
