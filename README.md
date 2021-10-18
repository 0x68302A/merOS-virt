### merOS - Build and interact with a set of virtual machines.

## NOTE: CURRENTLY OPERATIONAL ONLY UNDER DEBIAN ( AND BASED ) x86 SYSTEMS

### SYNOPSIS

**merOS** can be used to: 

- Bootstrap, a base installation- Chroot of currently A) Alpine or B) Debian Linux
	
- Populate, this Chroot with a custom set of configuration files

- Pack the Chroot Rootfs, under a qemu image

- Virtualize the system- Target

- Network/ Netfilter a set of Targets with/ without a DNS resolver.

merOS can also be used  with its' own included set of Firewall- Guest VMs - "*mersec*"
A VM-set inspired from the Whonix project, but with flexibility,
minimalist configuration, and light- weightness in mind.

**It should be noted though, that this project is under heavy development, and should be used with caution.**

### DESCRIPTION

Families are used to describe sets of systems,
and Targets are the individual Virtualized Machines.

Configuration files are found, and should be placed,
under ./conf/target/[fam-id]/ - containing:
	
1. The includes.chroot custom rootfs directory
	under /rootfs/[target-id]/

2. Build XML conf files which describe target properties
	under /build/[target-id]

3. Network & Firewall hooks
	under /hooks/

4. Libvirt XML conf files, for which some
	properties are modified on runtime.
	under /libvirt/[target-id]

**The included "*mersec*" configuration set can be used
as a template, as to create any other set of systems.**


### SYSTEM PREPERATION

You can run meros.py --setup,
or manually resolve dependancies,
and a dir tree creation

custom merOS created data are found
under ./data/


### BUILD && MANAGE A VM
	

[vm-full-id] refers to the
[fam-id] + [vm-id] parameters
of the Target.	

---kernel-build
Builds the Linux kernel, based on host Arch.
Custom .config kernel configuration options
can be set.
	
--get [alpine]
Grab the base rootfs, from oficcial mirrors
Debian will also be availabe, after some polishing.

--build [vm-full-id]
This creates and populates the rootfs chroot
and builds the qemu compatible .qcow image.
Result images are found under ./data/images/

--init [vm-full-id]
Initialize Target Networks
and machines.

--shutdown
Currently halts as libvirt guests.
	

### COMMUNICATING WITH A VM

--connect [vm-full-id]

--push [vm-full-id] [file/ folder] 

--pull [vm-full-id]
Pull all files from @[target-id]:~/mos-shared/
to ./data/mos-shared/[vm-full-id]

--sync [vm-full-id]
Pull & Push all files from mos-guest:/mos-shared/
to ./data/mos-shared/[vm-full-id]


### CONTRIBUTING

I am by no means a professional developer.
This is a project in which I hope to learn, and share ideas-
concepts and practical solutions to development and
modern privacy and management problems.

Any contributions are welcome, you're encouraged to create tickets, pull requests
or offer any ideas on the project!

You can also donate on: BTC-ADDRESS

COPYRIGHT

License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.
