# meros


## SYNOPSIS
**meros** – a minimal toolkit for - *declaratively* - building, provisioning, and interconnecting local Virtual Machines.

## DESCRIPTION

`meros` is a tool for managing local VMs through a combination of declarative configuration files and automated orchestration. It provides a unified interface for building root filesystem images, compiling the Linux Kernel, and running QEMU-based virtual machines, all defined through a simple YAML manifest.

The system is designed for fast iteration, cross-platform testing, and low-overhead provisioning, focused on remaining auditable and flexible. It adopts key ideas from tools like **debootstrap**, **Docker**, **Packer**, **Vagrant**, and **Ansible**, but focuses exclusively on local, Linux-hosted workflows with zero daemons, and minimal dependencies.


## PHILOSOPHY

The core philosophy is to provide **local runtime agility** without introducing heavy abstractions.
Rather than reinventing the stack, `meros` wraps common Linux utilities such as `qemu` and networking tools – into a declarative, reproducible lifecycle manager.

The project favors:

- **Simplicity** - over feature-bloat.
- **Transparency** - over automation magic.
- **Local-first tooling** - for fast feedback loops.
- **Single-purpose composability** - avoiding implicit infrastructure.

Each VM Group is described by a **constellation**, a YAML document that defines how an image shall be built, and how the system should be launched.

This approach enables flexible and predictable provisioning across local machines without requiring external infrastructure.


## ARCHITECTURE

At its core, `meros` consists of the following phases:

1. **Kernel Compilation**
   Uses upstream Linux sources to build a fresh kernel via `make`. Output goes to `./data/disks/bzImage`.

2. **Root Filesystem/ Full Image Creation**
   Uses `debootstrap` (or plain distro rootfs archives) to create a base image. Augmented by user-defined files (`includes.choot/`) and shell scripts (`hooks/`). Result is a `qcow2` root disk per VM.

3. **Runtime Launching via QEMU**
   Spawns one or more VMs using `qemu-system-x86_64`, networking via `bridge` and `nftables`, with optional Wayland GUI forwarding via `waypipe`.

4. **Manifest-Driven Orchestration**
   Everything is controlled through a YAML manifest per constellation. This includes VM names, disk sizes, network setup, kernel parameters, and optional mounts or forwarding.

No external services or agents are required. Everything runs locally and predictably.


## GETTING STARTED

### Dependencies

- `python3`
- `qemu-system-x86_64`
- `qemu-img`
- `debootstrap` or `apk-tools`
- `bridge-utils` / `iproute2`
- `nftables`
- Optional: `waypipe` (for GUI apps passthrough to host)

Install them using your package manager or run:

```bash
sudo ./dist-conf.sh
```

### Setup

```bash
git clone recursive https://github.com/0x68302A/merOS-virt
cd merOS-virt
python3 -m venv venv --system-site-packages
pip install -e .
```

## USAGE

### 1. Build the Kernel

```bash
meros kernel-build
```

Builds a minimal Linux kernel, and places the bzImage in ./data/disks/bzImage.

### 2. Create a constellation


```bash
cp -r examples/my_constellation constellations/
```

The constellation directory should include:

- my_constellation.yml – The manifest
- includes.choot/ – files to copy into the rootfs
- hooks/ – optional build-time scripts (post-install, finalize etc.)

Example manifest:

```bash
bridges:
  bridge_name:
    subnet: "10.0.10.0/24"
    policy_type: host-access ## Or: `isolated`
    allowed_ports: [22, 80, 443] ## Optional
    allowed_ips: [192.168.100.0/24] ## Optional


virtual_machines: vm_name:
    arch: "x86_64" ## Appended to: `qemu-system-`
    distribution: debian ## Optional: Used with `build --rotfs-img`
    disk_size: 2G
    memory: 512
    cpus: 1
    networks:
      - label: tap_vmname_01_
        bridge: bridge_name ## Refference to `bridge_name`
        ip_addr: "10.0.10.21"
        model: virtio-net-pci
```

### 3. Build rootfs image

```bash
meros build --rootfs-img my_constellation
```

Or to reuse a previous image:

```bash
meros build --use existing-image.qcow2 my_constellation vm_name
```

### 4. Launch the VM(s)

```bash
meros init my_constellation
```

VMs start with bridge networking and no serial console access.

## EXAMPLES

### Alpine with GUI forwarding


```bash
meros build alpine-gui
meros push alpine-gui vm_name local_dir
meros run alpine-gui vm_name remote_application
```

Build the `alpine-gui` constellation, pushes a local file to the VM, launches an X11/Wayland GUI tunneled application over Waypipe.


### Multi-VM constellation

```bash
meros init lab_network
meros connect lab_network vm_name
```

Defines a small lab of VMs connected via bridged networking for simulating cross-system behaviors, connects to the VM via SSH,.


## BENEFITS

- Cross-Platform Testing
  Boot multiple Linux distros on the same host with different kernels and filesystems.

- Minimal Runtime Overhead
  Uses only standard CLI tools with no background agents or daemons.

- Rapid Development Cycles
  Constellation manifests are versionable and easy to duplicate.

- Flexible GUI/Network Modes
  Run headless, forward GUIs via Waypipe, or test networked configurations locally.


## LIMITATIONS

- No automatic snapshotting or long-term storage integration
- Designed for developers and admins comfortable with the Linux CLI


## LICENSE

GPL. See LICENSE file.
