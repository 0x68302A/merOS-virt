### merOS - <br>
##### Build and interact with a set of Virtual Machines.

### SYNOPSIS

**merOS** can be used to:

- **Bootstrap**, a base installation (**Chroot**) of A) **Alpine** or B) **Debian** Linux.
	
- **Populate**, the Chroot with a custom set of configuration files and packages.

- **Pack the the Chroot**, under a qemu image.

- **Virtualize** the Chroot- Thereof, Target.

- **Network/ Netfilter** a set of Targets with/ without a DNS resolver.

### DESCRIPTION

**Families are used to describe sets of Targets ( *Virtualized Machines* )**

**Family configuration files** are found, and should be placed,
under conf/target/[fam-id]/ - containing:
	
1. **The Target rootfs directory**,
	under rootfs/[target-id]/includes.chroot/ -
	*This is where any custom package configuration, or persistent data, can be placed.*

2. **The Target build-time hooks directory**, 
	under rootfs/[target-id]/hooks/
	*This is where any shell script can be placed- It is run in the Target Chroot, before build.*
	
3. **Build XML configuration files**,
	under build/[target-id].xml
	*This is where Target properties are described, such as distro, free size, etc*

4. **Host run-Time hooks**
	under hooks/
	*This is where host run-time hooks can be found- These are executed upon Family initialization.* 

5. **Libvirt XML configuration files**, for which some
	properties are modified on runtime.
	under libvirt/[target-id].xml
	*The standard libvirt-style XMLs.*

Two Family Templates, currently in beta development,
are: ***mos\_mersec  and mos\_mersec_deb*** -
Currently included as submodules in our main Repository


### SYSTEM PREPERATION

You can run setup.sh

Or manually resolve dependencies,
and create a dir tree, as found inside mos/host_conf.py

**Custom merOS created data** are found
under data/


### BUILD && MANAGE A VM
	
> --build [fam-id]

This creates and populates the rootfs chroot dir,
builds the qemu compatible .qcow image, which can be found under
data/images/

> --init [fam-id]

Initialize Target VMs and Networks.

> --shutdown

Currently **halts **ALL** libvirt guests**.
	

### COMMUNICATING WITH A VM

**vm-full-id = [fam-id + '-' + target-id]
**(ex. *mos_mersec_deb-guest*)

> --connect [vm-full-id]

SSH into Target.

> --push [vm-full-id] [file/ folder]

Copy file to Target ( Defaults to ~/.mos-shared/* )

> --pull [vm-full-id]

Pull all files from Targets' ~/mos-shared/
to data/mos-shared/[vm-full-id]


### CONTRIBUTING

**I am by no means a professional developer.**
This is a project in which I hope to learn, and share ideas-
concepts and practical solutions to development and
modern privacy and management problems.

Any contributions are welcome, you're encouraged to create tickets, pull requests
or offer any ideas on the project!

You can also donate on: BTC-ADDRESS

COPYRIGHT

License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.

#### Note, currently supporting *only Debian-based x86* hosts
******