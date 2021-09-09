NAME

	merOS - Build and interact with a set of virtual machines.


SYNOPSIS

	merOS can be used to: 

	Bootstrap, a base installation of currently A) Alpine or B) Debian Linux-
	Populate a chroot, with a custom set of configuration files
	under a foldering tree as found in debian-live-build-
	Pack the rootfs, under a qemu image-
	Virtualize the system- Target-
	Network/ Netfilter a set of Targets with/ without a DNS resolver.

	merOS can also be used  with its' own included set of Firewall- Guest VMs - "mersec"
	A VM-set inspired from the Whonix project, but with flexibility,
	minimalist configuration, and light-weightness in mind.

	This project is under heavy developmnent, and should be used with caution.


DESCRIPTION

	Families are used to describe sets of systems,
	and Targets are the individual Virtualized Machines.

	Configuration files are found
	under ./conf/target/[fam_id]/ - and contain:
	
	1. The includes.chroot custom rootfs directory
	under ./conf/target/[fam_id]/rootfs/[target_id]/

	3. Build XML conf files which describe target properties
	under ./conf/target/[fam_id]/build/[target_id]

	4. Network & Firewall hooks
	under ./conf/target/[fam_id]/hooks/

	5. Libvirt XML conf files, for which some
	properties are modified on runtime.
	under ./conf/target/[fam_id]/libvirt/[target_id]

	The included "mersec" configuration set can be used
	as a template, as to create any other set of systems.


SYSTEM PREPERATION

	You can run meros.py --setup,
	or manually resolve dependancies,
	and a dir tree creation

	Custom merOS created data are found
	under ./data/


BUILD && MANAGE A VM
	

	[vm_full_id] refers to the
	[fam_id] + [vm_id] parameters
	of the Target.	


	--build-kernel
	Builds the Linux kernel, based on host Arch.
	Custom .config kernel configuration options
	can be set.
	
	--get [alpine]
	Grab the base rootfs, from oficcial mirrors
	Debian will also be availabe, after some polishing.

	--build [vm_full_id]
	This creates and populates the rootfs chroot
	and builds the qemu compatible .qcow image.
	Result images are found under ./data/images/

	--init [vm_full_id]
	Initialize Target Networks
	and machines.

	--shutdown
	Currently halts as libvirt guests.
	

COMMUNICATING WITH A VM

	--connect [vm_full_id]

	--push [file/ folder] [vm_full_id]

	--pull [vm_full_id]
	Pull all files from @[target_id]:/mos-shared/
	to ./data/mos-shared/[vm_full_id]

	--sync [vm_full_id]
	Pull & Push all files from mos-guest:/mos-shared/
	to ./data/mos-shared/[vm_full_id]


CONTRIBUTING

	I am by no means a professional developer.
	This is a project in which I hope to learn, and share ideas-
	concepts and practical solutions to development and
	modern privacy and management problems.

	Any contributions are welcome, you're encouraged to create tickets, pull requests
	or offer any ideas on the project!

	You can also donate on: BTC_ADDRESS


COPYRIGHT

	License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
	This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.
