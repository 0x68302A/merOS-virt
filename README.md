### merOS - Build and interact with a set of virtual machines- Targets

### SYNOPSIS

**merOS** can be used to: 

- Bootstrap, a base installation (Chroot) of A) Alpine or B) Debian Linux.
	
- Populate, the Chroot with a custom set of configuration files and packages.

- Pack the the Chroot, under a qemu image.

- Virtualize the Chroot- Thereof, Target.

- Network/ Netfilter a set of Targets with/ without a DNS resolver.

### DESCRIPTION

Families are used to describe sets of Targets (Systems)

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

 "*mersec*" is a Family, consisting of two Targets, that we are currently maintaining.
A VM-set inspired from the Whonix project, but with flexibility,
minimalist configuration, and light- weightness in mind.
**This project is under heavy development, and should be used with caution.**



### SYSTEM PREPERATION

You can run setup.sh,
or manually resolve dependancies,
and create a dir tree, as found inside

Custom merOS created data are found
under ./data/


### BUILD && MANAGE A VM
	
--build [Family_ID]
This creates and populates the rootfs chroot
and builds the qemu compatible .qcow image.
Result images are found under ./data/images/

--init [Family_ID]
Initialize Target Networks
and machines.

--shutdown
Currently halts as libvirt guests.
	

### COMMUNICATING WITH A VM

--connect [Family_ID + Target_ID]

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

### Note, currently supporting only debian-based x86 systems