## merOS :: Build and Interact with a Set of Virtual Machines<br>

### SYNOPSIS

**merOS** can be used to:

- **Bootstrap**, a base installation - <br> **Chroot** of A) **Debian** or B) **Alpine** Linux.
	
- **Populate**, the Chroot with a custom set <br> Of configuration **Files and Packages**.

- **Pack** the the Resulting Filesystem, <br> Under a **Qemu image**.

- **Virtualize** the Final Image/ VM- <br> Thereof, **Target**.

- **Network/ Netfilter** resulting Targets.

---
### DESCRIPTION

**merOS:** <br>

Not unlike Debootstrap *(which we also use)*, **allows for fine- grained build control over a structure of a file-system-**<br>
Not unlike Virtualbox, **allows for ease of access to a number of Virtual Machines-** <br>
Not unlike Docker,**allows for secure application testing-** <br>
Not unlike Qubes OS,**allows for secure activity-based compartmentalization of activities.**

**merOS Families:** <br>

Provide **a simple, XML and file-based configuration file-set**. <br>
From a build **recipe-like structure**, they allow us to set-up a full **set of virtualized machines,<br> 
with an abstraction layer around Building, Virtualization, Networking and Connection.** <br>

---
### ARCHITECTURE

**Families are used to describe Sets of Targets ( VMs )**

**Configuration Files** are found, and should be placed,
under: <br> `conf/target/[fam-id]/` - containing:
	
1. **The Target rootfs directory** : `rootfs/[target-id]/includes.chroot/` <br>
	Where any custom package configuration file, or persistent data, can be placed. <br>
	( Inspired by the [Debootstrap](https://debian-live-config.readthedocs.io/en/latest/custom.html#config-includes-chroot) Debian-Building architecture. )


1. **The Target build-time hooks directory** : `rootfs/[target-id]/hooks/ `<br>
	Where a shell script can be placed and is run in the Target Chroot, before build. <br>
	( Inspired by the [Debootstrap](https://debian-live-config.readthedocs.io/en/latest/custom.html#config-hooks) Debian-Building architecture. )

3. **Build XML configuration files** : `build/[target-id].xml` <br>
	Where Target properties are described, <br> such as Distro, Image Free Size, etc.

4. **Host run-Time hooks** : `hooks/` <br>
	Where Host run-time hooks can be found- <br >These are executed upon Family initialization.

5. **Libvirt XML configuration files** : `libvirt/[target-id].xml`<br>
	Describing Virtual Machine Emulation options. <br>
	(As used by [libvirt-Domains](https://libvirt.org/formatdomain.html) and
	[libvirt-Networks](https://libvirt.org/formatnetwork.html)
	

**Two Family Templates, currently in beta development, are:** <br>

- `mos_sec` A Whonix- like set of two Targets (VMs) || Firewall & Guest.
- `mos_lab` A Whonix/ Kali- like set of three Targets (VMs) || Firewall & Tool  Guest.

***Both are currently included as sub-modules in our main Repository***

**A fully transparent, but critical, part of building a Target** (VM)-	is the **Linux Kernel Cloning and Building.** <br>
	This step could as well be skipped, and replaced with a **precompiled kernel-image download,
	reducing bandwidth/ processing use-** <br> but leaving a significant part of the running machine out of our control. <br>
	(Such an option could/ should nevertheless be implemented )

---
### SYSTEM PREPARATIONoptimized

**All merOS created data** are placed
under: `./data/[fam_id]`<br>

- Clone the project, along with it's submodules: <br>
`git clone --recursive`<br>

- Run `./dist-conf.sh` - or: <br>
	**Manually resolve any system/ distro-specific dependencies- <br>
	See below.** <br>

- Install the project, for all users: <br>
	`sudo pip3 install -e --system` <br>

**You can now call `meros`** !



---
### SYSTEM DEPENDENCIES

**Are aquired  through `./dist-conf.sh`** <br>

- **Python3** <br>
	After initially implementing this idea in bash, <br>
	Python3 is chosen for its' **wide availability on machines,** <br>
	**ease of understanding- auditing and contributing.**
	
- **[Debootstrap](https://wiki.debian.org/Debootstrap)** <br>
	Is used for the Debian Target **Rootfs building.** <br>
	Being activelly-maintained by the Debian team, <br>
	and greatly adopted-	( *Just think of Debian-based OSes* ) <br>
	Along with bringing the **security and stability** of Debian- <br>
	It was chosen for the **basic flavor for merOS-based Targets.**

- **[Libvirt](https://libvirt.org/)** <br>
	Is used as the main virtualization platform. <br>
	Being actively-maintained, widely implemented and **documented thoroughly** -<br> 
	It was chosen as most appropriate **Virtualization framework for this project.**
	
- **[Xpra](https://www.xpra.org/)** <br>
	Is used as the main SSH- x11 communication framework, <br>
	used with `--run` and `--connect|-c`. <br>
	Being actively maintained, and well documented- it allows for a reliable and faster, <br>
	more secure way of XForward-like functions.

---
### BUILDING & MANAGING A TARGET ( VM )

`[fam-id]` - `[target-id]` = `target-full-id`  ( ex. `mos_sec-guest` )  <br>

- `--build` `[fam-id]` <br>
This **creates and populates** the rootfs chroot dir, <br>
and **builds** the qemu compatible .qcow image- <br> 
Which can be found under: `data/images/`

- `--init|-i` `[fam-id]` <br>
**Initialize** Targets and Networks via Libvirt.

- `--shutdown` <br>
( Currently **halts ALL Libvirt guests** )

The **recommended free-space for the project sits at around 12- 15GB ( For `mos_lab` )** - <br>
With the possibility to **free up to ~92% after initial build** - <br> **By  a simple `rm -rf` of `./data/build/bootstrap/[fam_id]`**. <br>
**Since the final image** resides under: `./data/images/[target-full-id]`

---
### COMMUNICATING WITH A VM

**The following require an SSH server set-up on the Target ( VM ) Side, <br> Along with an active network connection with the host** ( *As found in mos_mersec* )


-  `--connect` `[vm-full-id]`<br>
SSH into Targets' defined user ( *As found under:* `$CONF/build/[target-id]` )

-  `--run` `[vm-full-id]` `[VMs-executable]`<br>
ex. `mos_sec-guest --run firefox`

- `--push` `[vm-full-id]` `[file/ folder]`<br>
Copy file to Target ( *Defaults transfers to VMs Users'* `~/.mos-shared/` )

- `--pull` `[vm-full-id]` <br>
Pull all files from Targets' `~/mos-shared/` <br>
to `./data/mos-shared/[vm-full-id]`


---
### CONTRIBUTING

**I am by no means a professional developer.** <br>
This is a project in which I hope to learn, and share ideas-
concepts and practical solutions <br> 
to development and
modern privacy and management problems.

Any contributions are welcome, you're encouraged to create tickets, <br>
pull requests
or offer any ideas on the project!
 
---
### COPYRIGHT

License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>. <br>
This is free software: you are free to change and redistribute it.<br> 
There is NO WARRANTY, to the extent permitted by law.

---
### IMPORTANT NOTES:
	Being an actively developed, actively maintained project- No security guarantee is provided.
	Bugs are to be expected, implementations ( secure-critical or not ) may be broken.
	And as always, security issues may arise from within the selected frameworks used-
	no matter how widely adopted, or thoroughly tested they be.
