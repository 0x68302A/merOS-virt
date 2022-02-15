## merOS :: Build and Interact with a Set of Virtual Machines<br>

### SYNOPSIS

**merOS** can be used to:

- **Bootstrap**, a base installation - **Chroot** of A) **Alpine** or B) **Debian** Linux.
	
- **Populate**, the Chroot with a custom set of configuration Files and Packages.

- **Pack the the Resulting Filesystem**, under a qemu image.

- **Virtualize** the Final Image- Thereof, **Target**.

- **Network/ Netfilter** a set of Targets with/ without a DNS resolver.

## <br>

### DESCRIPTION

**Families are used to describe Sets of Targets ( *Virtualized Machines* )**

**Configuration files** are found, and should be placed,
under `conf/target/[fam-id]/` - containing:
	
1. **The Target rootfs directory** :: `rootfs/[target-id]/includes.chroot/` <br>
	Where any custom package configuration file, or persistent data, can be placed.


1. **The Target build-time hooks directory** :: `rootfs/[target-id]/hooks/ `<br>
	Where a shell script can be placed and is run in the Target Chroot, before build.

3. **Build XML configuration files** :: `build/[target-id].xml` <br>
	Where Target properties are described, such as Distro, Image Free Size, etc.

4. **Host run-Time hooks** :: `hooks/` <br>
	Where Host run-time hooks can be found- These are executed upon Family initialization.

5. **Libvirt XML configuration files** :: `libvirt/[target-id].xml`<br>
Describing Virtual Machine Emulation options.

---
**Two Family Templates, currently in beta development,
are:**`mos_sec` (Included as a submodule)  and `mos_mersec` ( The alpine version of mos_sec )- <br>
*Currently included as submodules in our main Repository*
## <br>
---

### SYSTEM PREPERATION

You can run `./dist-conf.sh` - 
or <br>
manually resolve any distro-specific dependencies. <br>
  
Clone the project, along with it's submodules- <br>
`git clone --recursive` <br>

Install the project. <br>
`pip install -e .` <br>

You can now call `meros` !

The **recommended space** for the project sits at **around 12- 15GB** - <br>
With the possibility to **free up to 8- 10GB after initial set-up**. <br>

**Custom merOS created data** will be placed
under `./data/`<br>

---

### BUILD && MANAGE A VM
	
> --build `[fam-id]`

This creates and populates the rootfs chroot dir,
builds the qemu compatible .qcow image, which can be found under
data/images/

> --init `[fam-id]`

Initialize Target VMs and Networks.

> --shutdown

Currently **halts *ALL* libvirt guests**.

## <br>

### COMMUNICATING WITH A VM

`vm-full-id` = `[fam-id]` + '-' + `[target-id]`:: 
(ex. `mos_sec-guest`) 

**The following are require an SSH server on the Target Side, along with an active network connection** (*As found in mos_merec*)

> --connect `[vm-full-id]`

SSH into Target.

> --push `[vm-full-id]` `[file/ folder]`

Copy file to Target ( Pastes to ~/.mos-shared/* )

> --pull `[vm-full-id]`

Pull all files from Targets' `~/mos-shared/`
to `data/mos-shared/[vm-full-id]`

## <br>


### CONTRIBUTING

**I am by no means a professional developer.** <br>
This is a project in which I hope to learn, and share ideas-
concepts and practical solutions <br> 
to development and
modern privacy and management problems.

Any contributions are welcome, you're encouraged to create tickets, <br>
pull requests
or offer any ideas on the project!

You can also donate on: `BTC-ADDRESS`  

---

### COPYRIGHT

License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>. <br>
This is free software: you are free to change and redistribute it.<br> 
There is NO WARRANTY, to the extent permitted by law.

---
#### Note, currently supporting *only Debian-based x86* hosts
******
