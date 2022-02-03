### merOS - <br>
##### Build and interact with a set of Virtual Machines- Targets

### SYNOPSIS

**merOS** can be used to:

- **Bootstrap**, a base installation (**Chroot**) of A) **Alpine** or B) **Debian** Linux.
	
- **Populate**, the Chroot with a custom set of configuration files and packages.

- **Pack the the Chroot**, under a qemu image.

- **Virtualize** the Chroot- Thereof, Target.

- **Network/ Netfilter** a set of Targets with/ without a DNS resolver.

### DESCRIPTION

**Families are used to describe sets of Targets (Virtualized Machines)**

**Family configuration files** are found, and should be placed,
under ./conf/target/[fam-id]/ - containing:
	
1. **The custom rootfs directory**, includes.chroot and build-time hooks
	under /rootfs/[target-id]/

2. **Build XML configuration files** which describe target properties
	under /build/[target-id]

3. **Host Family Run-Time hooks**
	under /hooks/

4. **Libvirt XML conf files**, for which some
	properties are modified on runtime.
	under /libvirt/[target-id]

Two Family-Templates, currently in beta development,
are: ***mos\_mersec  and mos\_mersec_deb*** -
Currently included as submodules in our main Repository


### SYSTEM PREPERATION

You can run setup.sh
or manually resolve dependancies,
and create a dir tree, as found inside

**Custom merOS created data** are found
under ./data/


### BUILD && MANAGE A VM
	
> --build [fam-id]

This creates and populates the rootfs chroot
and builds the qemu compatible .qcow image.
Result images are found under ./data/images/

> --init [fam-id]

Initialize Target Networks
and machines.

> --shutdown

Currently **halts as libvirt guests**.
	

### COMMUNICATING WITH A VM

vm-full-id = [fam-id + '-' + target-id]
(ex. *mos_mersec_deb-guest*)

> --connect [vm-full-id]

> --push [vm-full-id] [file/ folder]

> --pull [vm-full-id]

Pull all files from @[target-id]:~/mos-shared/
to ./data/mos-shared/[vm-full-id]

> --sync [vm-full-id]

Pull & Push all files from mos-guest:/mos-shared/
to ./data/mos-shared/[vm-full-id]


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

#### Note, currently supporting only Debian-based x86 systems
******