Title: Using Vagrant with Solaris 11
Date: 2014-02-19 23:23
Tags: solaris,vagrant
Category: solaris
Slug: vagrant_solaris11
Author: William Van Hevelingen
Summary: Using Vagrant with Solaris 11

I finally got Solaris 11 vagrant boxes working! 

First you need to download a Solaris 11 iso from Oracle's website. Then use packer to build a solaris11 box file which is explained in Alan Chalmer's [blog](http://resilvered.blogspot.com/2014/02/solaris-vagrant-packer-and-base-box.html).

Next we need a Vagrantfile, you can pull down mine and modify it for your needs. Then create an iso directory and place your solaris box image in it.

    :::bash
    git clone https://gist.github.com/9108604.git
    mkdir iso
    cp /packer/build/directory/packer_solaris-11.1-amd64_virtualbox.box iso/

Our Vagrantfile looks like this. To mirror a production setup we are creating a secondary disk on the IDE controller to mirror rpool. Then we create a SATA controller and attach six 1G disks.

[gist:id=9108604]

Now that we have everything we need we can start the vm with vagrant up.

    :::bash
    vagrant up
    Bringing machine 'sunosfiler' up with 'virtualbox' provider...
    [sunosfiler] Box 'solaris-11.1' was not found. Fetching box from specified URL for
    the provider 'virtualbox'. Note that if the URL does not have
    a box for this provider, you should interrupt Vagrant now and add
    the box yourself. Otherwise Vagrant will attempt to download the
    full box prior to discovering this error.
    Downloading or copying the box...
    Extracting box...te: 25.0M/s, Estimated time remaining: 0:00:01)
    Successfully added box 'solaris-11.1' with provider 'virtualbox'!
    [sunosfiler] Importing base box 'solaris-11.1'...
    [sunosfiler] Matching MAC address for NAT networking...
    [sunosfiler] Setting the name of the VM...
    [sunosfiler] Setting the name of the VM...
    [sunosfiler] Clearing any previously set forwarded ports...
    [sunosfiler] Creating shared folders metadata...
    [sunosfiler] Clearing any previously set network interfaces...
    [sunosfiler] Preparing network interfaces based on configuration...
    [sunosfiler] Forwarding ports...
    [sunosfiler] -- 22 => 2222 (adapter 1)
    [sunosfiler] Running any VM customizations...
    [sunosfiler] Booting VM...
    [sunosfiler] Waiting for VM to boot. This can take a few minutes.
    [sunosfiler] VM booted and ready for use!
    [sunosfiler] Setting hostname...


Now we login and become the root user.

    :::bash
    vagrant ssh
    sudo -i

Next let's take a look at the disks that we attached. You can use the format command to list the availible disks.

    :::bash
    format
    Searching for disks...done


    AVAILABLE DISK SELECTIONS:
           0. c7d0 <VBOX HAR-bafb5063-0735aa9-0001-8.00GB>
              /pci@0,0/pci-ide@1,1/ide@0/cmdk@0,0
           1. c8d0 <VBOX HAR-196ca772-16ab95f-0001 cyl 4093 alt 2 hd 128 sec 32>
              /pci@0,0/pci-ide@1,1/ide@1/cmdk@0,0
           2. c9t1d0 <ATA-VBOX HARDDISK-1.0 cyl 1022 alt 2 hd 64 sec 32>
              /pci@0,0/pci8086,2829@d/disk@1,0
           3. c9t2d0 <ATA-VBOX HARDDISK-1.0 cyl 1022 alt 2 hd 64 sec 32>
              /pci@0,0/pci8086,2829@d/disk@2,0
           4. c9t3d0 <ATA-VBOX HARDDISK-1.0 cyl 1022 alt 2 hd 64 sec 32>
              /pci@0,0/pci8086,2829@d/disk@3,0
           5. c9t4d0 <ATA-VBOX HARDDISK-1.0 cyl 1022 alt 2 hd 64 sec 32>
              /pci@0,0/pci8086,2829@d/disk@4,0
           6. c9t5d0 <ATA-VBOX HARDDISK-1.0 cyl 1022 alt 2 hd 64 sec 32>
              /pci@0,0/pci8086,2829@d/disk@5,0
           7. c9t6d0 <ATA-VBOX HARDDISK-1.0 cyl 1022 alt 2 hd 64 sec 32>
              /pci@0,0/pci8086,2829@d/disk@6,0
    Specify disk (enter its number): 

You can see that c7d0 and c8d0 are our 8G system disks attached to the IDE controller. Let's attach c8d0 to the rpool and make a mirror.

    :::bash
    zpool attach rpool c7d0 c8d0
    Make sure to wait until resilver is done before rebooting.

If we examine the pool now, we can see it resilvering.

    zpool status rpool
      pool: rpool
     state: DEGRADED
    status: One or more devices is currently being resilvered.  The pool will
            continue to function in a degraded state.
    action: Wait for the resilver to complete.
            Run 'zpool status -v' to see device specific details.
      scan: resilver in progress since Thu Feb 20 19:14:00 2014
        809M scanned out of 3.69G at 38.5M/s, 0h1m to go
        777M resilvered, 21.40% done
    config:

            NAME        STATE     READ WRITE CKSUM
            rpool       DEGRADED     0     0     0
              mirror-0  DEGRADED     0     0     0
                c7d0    ONLINE       0     0     0
                c8d0    DEGRADED     0     0     0  (resilvering)

    errors: No known data errors

After a few minutes it should be fully online. Then we need to install grub on the new disk

    :::bash
    bootadm install-bootloader -P rpool

Now that our root pool is setup we can move on to our storage pool. I choose to mirror every disk but you can choose whatever raid configuration you prefer.

    :::bash
    zpool create stark mirror c9t1d0 c9t2d0 mirror c9t3d0 c9t4d0 mirror c9t5d0 c9t6d0
    zpool status stark
      pool: stark
     state: ONLINE
      scan: none requested
    config:

            NAME        STATE     READ WRITE CKSUM
            stark       ONLINE       0     0     0
              mirror-0  ONLINE       0     0     0
                c9t1d0  ONLINE       0     0     0
                c9t2d0  ONLINE       0     0     0
              mirror-1  ONLINE       0     0     0
                c9t3d0  ONLINE       0     0     0
                c9t4d0  ONLINE       0     0     0
              mirror-2  ONLINE       0     0     0
                c9t5d0  ONLINE       0     0     0
                c9t6d0  ONLINE       0     0     0

    errors: No known data errors

At this point our storage is configured and we can move on to creating filesystems, setting up services, or running tests.

Happy Hacking!
