**SYNOPSIS**

**merOS - <br /> Build && Interconnect a set of systems.**


`meros [OPTION]` <br />
Enter `meros -h` to display this page. <br />

**DESCRIPTION**

merOS can be used to: 

- **Bootstrap** a base installation of currently A) debian or B) alpine linux.
- **Populate** the bootstrap chroot with a custom set of configuration files.
under a foldering structure as used in debian live-build.
- **Pack the above fs** under a qemu image.
- **Virtualize** the system.
- **Network/ firewall** a set of VMs with/ without a DNS resolver.

merOS can also be used  with its' own included set of Firewall- Guest VMs - **"mos-priv".** <br />
This is a VM-set inspired **from the Whonix project**, but with flexibility,
minimalist configuration, and light-weightness in mind. <br />
This project is under heavy developmnent, and should be used with caution.

**SYSTEM CONFIGURATION**

`--setup` <br /> 
Set-up host ( dependencies - etc ) <br />
Configuration files are under ./etc/host/

**BUILDING && MANAGING A VM**
	
`--build-kernel` <br />
Builds the Linux kernel, based on host Arch. <br />
Custom .config kernel configuration files are <br />
under ./etc/conf/kernel/ <br />

`--bootstrap` <br />
Grab and bootstrap a clean base rootfs. <br />
The [DISTRO] variable is currently set <br />
under the meros script. <br />
 
`--build [VM_ID]` <br />
Builds the qemu compatible .qcow image. <br />


`-i|--init [VM-ID]` <br />
Start a VM, configured and built with meros. <br />

`--shutdown` <br />
Kill all qemu instances, deconfigure all bridges & NICs  <br />
and reset nftables - Reads fro ./etc/active
	
`build && init` utilize the configuration files found  <br />
under ./etc/conf/[VM-ID]/ containing: <br />

1. The includes.chroot directory <br />
in which custom rootfs files can be placed- <br />
 and in turn passed on in our build.
3. Build && init files for building and qemu managemenet <br >

3. Network && Firewall settings

3. A *.var file containing critical VM info

The included "mos-priv" configuration set may be used  <br />
as a template to create any other set of systems.

**COMMUNICATING WITH A VM**

Using [VM-ID] ssh credectials - as defined in <br />
./etc/conf/[VM-ID]/[VM-ID].var

`-c|--connect [VM-ID]`

`-p|--push [FILE/ FOLDER] [VM-ID]`

`--pull [VM-ID]` <br />
Pull all files from @mos-guest:/mos-shared/
to ./mos-shared/[VM_ID]

`-s|--sync [VM-ID]` <br />
Pull & Push all files from @mos-guest:/mos-shared/ <br />
to ./mos-shared/[VM_ID]

**CUSTOM IMAGE && NETWORK FUNCTIONS**

``--brinit [BRIDGE_ID]` <br />
Create a custom Bridge and attach a dns resolver.

`--brkill [BRIDGE_ID]` <br />
Kill and deconfigure Bridge

`--run [IMAGE] [BRIDGE_ID]` <br />
Run a custom .iso or .qcow image <br />


**CONTRIBUTE**

I am by no means a professional developer. <br />
This is a project in which I hope to learn, and share ideas-  <br />
concepts and practical solutions to development and  <br />
modern privacy problems.

Any contributions are welcome, you're encouraged to create tickets, pull requests <br />
and offer any ideas on the project!

You can also donate on: BTC_ADDRESS

**COPYRIGHT**

License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.
