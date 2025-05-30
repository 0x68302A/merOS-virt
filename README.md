## merOS-virt :: Build, Provision and Interact with Virtual Machine Sets

### SYNOPSIS

`meros` can be used to:

- **Make**, the `Linux kernel`

- **Build**, a `rootfs image` of `Debian` or `Alpine` Linux.

- **Configure**, the `rootfs` with a custom set of configuration `files`, `packages` and `build-time` scripts.

- **Patch** an existing `qcow2` image, with the same configuration items.

- **Pack** the the resulting filesystem, in a `qcow2` image.

- **Virtualize** the final VM image.

- **Network/ Netfilter** resulting Targets.

---
### DESCRIPTION

`meros` is designed as a virtualization *swiss knife*.

Using:
- qemu-system-[all]
- qemu-img
- net-tools
- nftables
- waypipe

**merOS-virt Constellations:**

Provide **a simple, YAML and file-based configuration file-set**.


From a `manifest.yml` **recipe-like structure**, they allow us to manage the lifecycle of a **set** of `virtual machines`.

---
### ARCHITECTURE

**Constellations are used to describe VM Groups (*Stars*) **

**Destination files** are found, and should be placed,
under: <br> `constellations/[constellation]/` - containing:

#### 1. **The Target rootfs path** : `rootfs/[vm_name]/includes.chroot/`


Where any custom package configuration file, or persistent data, can be placed.


( Inspired by the [Debootstrap](https://debian-live-config.readthedocs.io/en/latest/custom.html#config-includes-chroot) Debian-Building architecture. )


#### 2. **The VM build-time hooks path** : `rootfs/[vm_name]/hooks/`


Where a shell script can be placed and is run in the Target Chroot, before build.

( Inspired by the [Debootstrap](https://debian-live-config.readthedocs.io/en/latest/custom.html#config-hooks) Debian-Building architecture. )

#### 3. **Main YAML configuration file** : `manifest.yml`

Where Target properties are described, such as `distro`, `image_frees_ize`, etc.

**A fully transparent, but critical, part of building a Target** (VM)-	is the **Linux Kernel Cloning and Building.**


This step could as well be skipped, and replaced with a **precompiled kernel-image download,
reducing bandwidth/ processing use-** but leaving a significant part of the running machine out of our control.

(Such an option could/ should nevertheless be implemented )

---
### SYSTEM PREPARATION

**All merOS created data** are placed
  under: `./data/`

- Clone the project, along with it's submodules:
`git clone --recursive`

- Run `./dist-conf.sh` - or **Manually resolve any system/ distro-specific dependencies- See below.**

- Setup project:

  `python3 -m venv [venv_path] install --system-site-packages`

   `pip3 install -e .`

**You can now call `meros`** !


---
### SYSTEM DEPENDENCIES

**Are aquired  through `./dist-conf.sh`** <br>

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

---
### USAGE

SEE: `meros --help`

---
### COPYRIGHT

License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.

This is free software: you are free to change and redistribute it.

There is NO WARRANTY, to the extent permitted by law.

---
### IMPORTANT NOTES:
	Being an actively developed, actively maintained project- No security guarantee is provided.
	Bugs are to be expected, implementations ( secure-critical or not ) may be broken.
	And as always, security issues may arise from within the selected frameworks used-
	no matter how widely adopted, or thoroughly tested they be.
