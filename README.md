## NAME

**meros** - Build, Provision and Interact with VM groups


## SYNOPSIS

**meros** *command* [options/ VMs/ Groups]


## DESCRIPTION

**meros** is a *swiss army knife* for managing, provisioning and configuring access to - *and from* - locally-run Virtual Machines.

**meros** can `kernel-build`, the `Linux`, allowing for rootfs-only image use and individual kernel version/ future testing with a deterministically built rootfs. `build` allows the user to build complete filesystem (*--use an existing qcow2 image*), or `rootfs-only` images of `Debian` or `Alpine` Linux. When `build` is used, the rootfs is confiured with the custom set of configuration files (*As the rootfs structure is copied*), and build-time `hooks`. The resulting image is packed in a qcow2 image, as name in `manifest`

**meros** can the virtualize the host, using the relevant configuration settings in `manifest`.


## USAGE/ OPTIONS

`meros kernel-build`:

    Builds the Linux kernel, from the latest git commit.
    This, results in: `data/disks/bzImage`

`meros build (--rootfs-only | --use PATCH_IMAGE) *constellation* [vm_name]`:

    Builds the VM group (*constellation*), or, an individual VM.

    `--rootfs-only` results in a single qcow2 image, containing the rootfs.
    To run, this image needs a compatible `kernel`, as the one created with `kernel-build`

    `--use` takes advanted of an existing qcow2 image - which is cloned, and configured.

`meros init *constellation*`

    Initializes the VM group.

_TODO: more_

## ARCHITECTURE

### **meros** Constellations:

Are comprised of:
- A **YAML configuration file**, containing build/ run-time critical info, such as:
    - Networking options
    - Disk size/ format
    - _TODO: more_
- A **dir structure that contains**.
    - `includes.choot`: Which is copied directly on the VM image
    - `hooks`: Which is build-time executed on the VM OS

### **meros** VM Management:

_TODO: more_

### **meros** Network Management:

_TODO: more_

## SYSTEM PREPARATION

**All merOS created data** are placed
  under: `./data/`

- Clone the project, along with it's submodules:
`git clone --recursive`

- Run `./dist-conf.sh` - or **Manually resolve any system/ distro-specific dependencies- See below.**

- Setup project:

  `python3 -m venv [venv_path] install --system-site-packages`

  `pip3 install -e .`

**You can now call `meros`** !


## DEPENDANCIES
### SYSTEM

**meros** is merely an automation framework, arround the following tools:
- qemu-system-[all]
- qemu-img
- net-tools
- nftables
- waypipe

#### These, can be aquired  through `./dist-conf.sh`

- **Python3**

	After initially implementing this idea in bash,

	Python3 is chosen for its' **wide availability on machines, ease of understanding- auditing and contributing.**

- **[Debootstrap](https://wiki.debian.org/Debootstrap)**
	Is used for the Debian Target **Rootfs building.**

	Being activelly-maintained by the Debian team,

	and greatly adopted-	( *Just think of Debian-based OSes* )

	Along with bringing the **security and stability** of Debian-

	It was chosen for the **basic flavor for merOS-based Targets.**

- **[Waypipe](https://github.com/neonkore/waypipe/)**

	Is used as the main SSH- Wayland communication framework, <br>
	used with `--run` and `--connect|-c`.

	Being actively maintained, and well documented- it allows for a reliable and faster,	more secure way of XForward-like functions.


## COPYRIGHT

License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.

This is free software: you are free to change and redistribute it.

There is NO WARRANTY, to the extent permitted by law.
