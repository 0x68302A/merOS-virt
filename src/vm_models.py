import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
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
class BridgeConfig:
    name: str
    subnet: str = "10.10.10.0/24"
    policy_type: str = "host-access"  # host-access/isolated
    allowed_ports: List[int] = field(default_factory=lambda: [22, 80, 443])
    allowed_ips: str = "172.0.0.1"
    allow_icmp: bool = True
    auto_create: bool = True  # Create bridge if missing

@dataclass
class NetworkInterface:
    label: str
    bridge: str  # Reference to BridgeConfig.name
    model: str = "virtio"
    ip_addr: Optional[str] = None
    mac: Optional[str] = None

@dataclass
class VMConfig:
    name: str
    kernel: str = None
    distribution: Optional[str] = None
    arch: Optional[str] = "x86_64"
    memory: str = "2G"
    kvm: bool = True
    display: bool = False
    cpus: int = 2
    build_free_mb: Optional[int] = None
    disks: List[VirtualDisk] = field(default_factory=list)
    networks: List[NetworkInterface] = field(default_factory=list)
    extra_args: List[str] = field(default_factory=list)

    def __str__(self):
        return (f"VM(name={self.name}, memory={self.memory}, cpus={self.cpus}, "
                f"kvm={self.kvm}, display={self.display}, "
                f"distribution={self.distribution}, arch={self.arch}, "
                f"build_free_mb={self.build_free_mb}, "
                f"networks={[n.bridge for n in self.networks]})")  # Changed here

@dataclass
class Config:
    bridges: Dict[str, BridgeConfig]
    virtual_machines: Dict[str, VMConfig]

class VMConfigLoader:
    @staticmethod
    def load_config(path: Path) -> Config:
        with open(path) as f:
            data = yaml.safe_load(f)

        # Load bridges first
        bridges = {
            name: BridgeConfig(name=name, **cfg)
            for name, cfg in data.get('bridges', {}).items()
        }

        # Load VMs with bridge validation
        virtual_machines = {}
        for vm_name, vm_data in data['virtual_machines'].items():
            networks = []
            for net in vm_data.get('networks', []):
                bridge_name = net['bridge']
                if bridge_name not in bridges:
                    raise ValueError(f"Undefined bridge {bridge_name} for {vm_name}")
                networks.append(NetworkInterface(**net))

            virtual_machines[vm_name] = VMConfig(
                name=vm_name,
                networks=networks,
                memory=vm_data.get('memory', "2G"),
                kvm=vm_data.get('kvm', True),
                display=vm_data.get('display', False),
                distribution=vm_data.get('distribution', "None"),
                build_free_mb=vm_data.get('build_free_mb', "None"),
                arch=vm_data.get('arch', "x86_64"),
                cpus=vm_data.get('cpus', 2),
                kernel=vm_data.get('kernel', None),
                disks=[VirtualDisk(**d) for d in vm_data.get('disks', [])],
                extra_args=vm_data.get('extra_args', [])
            )

        return Config(
            bridges=bridges,
            virtual_machines=virtual_machines
        )
