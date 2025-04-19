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
class NetworkInterface:
    bridge: str = "br0"
    subnet: str = "10.10.10.255"
    model: str = "virtio"
    mac: Optional[str] = None

    def __str__(self):
        return f"Network(bridge={self.bridge},subnet={self.subnet}, model={self.model}, mac={self.mac})"

@dataclass
class VMConfig:
    name: str
    memory: str = "2G"
    kernel: str = None
    cpus: int = 2
    disks: List[VirtualDisk] = field(default_factory=list)
    network: NetworkInterface = field(default_factory=NetworkInterface)
    template: str = "default"
    extra_args: List[str] = field(default_factory=list)

    def __str__(self):
        return (f"VM(name={self.name}, memory={self.memory}, cpus={self.cpus}, "
                f"disks={len(self.disks)}, network={self.network}), kernel={self.kernel})")

class VMConfigLoader:
    @staticmethod
    def load_config(path: Path) -> Dict[str, VMConfig]:
        logger.info(f"Loading VM configuration from {path}")
        with open(path) as f:
            data = yaml.safe_load(f)
        
        templates = data.get('templates', {})
        vms = {}
        
        for vm_name, vm_data in data['virtual_machines'].items():
            template = templates.get(vm_data.get('template', 'default'), {})
            
            disks = [
                VirtualDisk(**disk) 
                for disk in vm_data.get('disks', [])
            ]
            
            network = NetworkInterface(
                **vm_data.get('network', template.get('network', {})))
            
            vms[vm_name] = VMConfig(
                name=vm_name,
                memory=vm_data.get('memory', template.get('memory', "2G")),
                cpus=vm_data.get('cpus', template.get('cpus', 2)),
                kernel=vm_data.get('kernel', template.get('kernel', None)),
                disks=disks,
                network=network,
                extra_args=vm_data.get('extra_args', [])
            )
            logger.debug(f"Loaded VM config: {vms[vm_name]}")
        
        logger.info(f"Loaded {len(vms)} VMs from configuration")
        return vms
