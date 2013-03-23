Title: Evacuating a Ganeti node for hardware diagnostics
Date: 2013-03-23 12:00
Tags: ganeti, kvm
Category: ganeti
Slug: evac-ganeti-node
Author: William Van Hevelingen
Summary: How to evacuate a Ganeti node for hardware diagnostics

One of the nodes in our Ganeti cluster was hanging on lvs commands and some of the instances were hanging while they wait for IO. I decided to be proactive and live migrate all of the instances off the node in order to bring it down for some debugging.

The following steps are how I brought the node offline with minimal downtime for production instances.

Overview of our cluster
-----------------------

* 4 nodes
* 46 instances
* Ubuntu 12.04 LTS
* Ganeti version 2.5.2-1
* Kvm version 1.0

Log into the master node
------------------------

Log into the master ganeti node.

    ssh nebula.cat.pdx.edu


Migrate the primary instances off suspect node 
----------------------------------------------

Run the gnt-node migrate command, passing in the node to migrate off of

    sudo gnt-node migrate katana.cat.pdx.edu

The output should look similar to this.

	root@claymore:~# gnt-node migrate katana
	Migrate instance(s) crystal.cat.pdx.edu, l1011.cat.pdx.edu,
	marauder.cat.pdx.edu, nyan.cat.pdx.edu, panic.cat.pdx.edu,
	receptacle.cat.pdx.edu, ruby.cat.pdx.edu, sapphire.cat.pdx.edu,
	webd.cat.pdx.edu, yermom.cat.pdx.edu, zeratul.cat.pdx.edu?
	y/[n]/?: y
	Submitted jobs 52820, 52821, 52822, 52823, 52824, 52825, 52826, 52827, 52828, 52829, 52830
	[...]
	Waiting for job 52825 ...
	Wed Mar 20 10:33:52 2013 Migrating instance crystal.cat.pdx.edu
	Wed Mar 20 10:33:52 2013 * checking disk consistency between source and target
	Wed Mar 20 10:33:56 2013 * switching node claymore.cat.pdx.edu to secondary mode
	Wed Mar 20 10:33:56 2013 * changing into standalone mode
	Wed Mar 20 10:34:58 2013 * changing disks into dual-master mode
	Wed Mar 20 10:35:01 2013 * wait until resync is done
	Wed Mar 20 10:35:02 2013 * preparing claymore.cat.pdx.edu to accept the instance
	Wed Mar 20 10:35:03 2013 * migrating instance to claymore.cat.pdx.edu
	Wed Mar 20 10:35:24 2013 * switching node katana.cat.pdx.edu to secondary mode
	Wed Mar 20 10:35:26 2013 * wait until resync is done
	Wed Mar 20 10:35:27 2013 * changing into standalone mode
	Wed Mar 20 10:35:27 2013 * changing disks into single-master mode
	Wed Mar 20 10:35:28 2013 * wait until resync is done
	Wed Mar 20 10:35:28 2013 * done
	[...]

Some of my instances failed to migrate properly.

	Wed Mar 20 10:33:16 2013 Migration failed, aborting
	[...]
	Job 52820 has failed: Failure: command execution error:
	Could not migrate instance sapphire.cat.pdx.edu: Failed to migrate instance: Too many 'info migrate' broken answers

Luckly these instances were not being used at the moment and I could use gnt-instance failover.

    # Warning! This will reboot the instance
    sudo gnt-instance failover sapphire.cat.pdx.edu


Evacuate secondaries using gnt-node
-----------------------------------

After the primaries have been migrated run the gnt-node evacuate command to move the secondaries.


    sudo gnt-node evacuate --secondary-only node2.cat.pdx.edu


gnt-node evacuate failed with a timeout error.
	
	sudo gnt-node evacuate --secondary-only katana
	Relocate instance(s) crystal.cat.pdx.edu, emerald.cat.pdx.edu,
	[...]
	y/[n]/?: y
	Wed Mar 20 11:16:49 2013  - INFO: Evacuating instances from node 'katana.cat.pdx.edu': crystal.cat.pdx.edu, emerald.cat.pdx.edu, fog.cat.pdx.edu, gameandwatch.cat.pdx.edu, l1011.cat.pdx.edu, log.cat.pdx.edu, marauder.cat.pdx.edu, nydus.cat.pdx.edu, panic.cat.pdx.edu, pika.cat.pdx.edu, receptacle.cat.pdx.edu, refinery.cat.pdx.edu, ruby.cat.pdx.edu, sapphire.cat.pdx.edu, void.cat.pdx.edu, warpgate.cat.pdx.edu, weba.cat.pdx.edu, webb.cat.pdx.edu, webc.cat.pdx.edu, webd.cat.pdx.edu, yermom.cat.pdx.edu, zeratul.cat.pdx.edu
	Failure: command execution error:
	Can't get data for node katana.cat.pdx.edu: Error 28: Operation timed out after 60910 milliseconds with 0 out of -1 bytes received

If gnt-node evacuate fails for you can evacuate secondaries per instance.


Evacuate the secondaries using gnt-instance
-----------------------------------

Locate the instances you want to move.

	sudo gnt-instance list -o name,pnode,snodes | grep katana

	gameandwatch.cat.pdx.edu claymore.cat.pdx.edu katana.cat.pdx.edu
	l1011.cat.pdx.edu        rapier.cat.pdx.edu   katana.cat.pdx.edu
	log.cat.pdx.edu          dirk.cat.pdx.edu     katana.cat.pdx.edu
	marauder.cat.pdx.edu     rapier.cat.pdx.edu   katana.cat.pdx.edu
	yermom.cat.pdx.edu       dirk.cat.pdx.edu     katana.cat.pdx.edu


Run gnt-instance replace-disks and give the name of another node that is not the primary of the instance.


    sudo gnt-instance replace-disks -n claymore.cat.pdx.edu yermom.cat.pdx.edu

The output will look similar to this:

	Wed Mar 20 13:24:39 2013 Replacing disk(s) 0 for yermom.cat.pdx.edu
	Wed Mar 20 13:24:39 2013 STEP 1/6 Check device existence
	Wed Mar 20 13:24:39 2013  - INFO: Checking disk/0 on rapier.cat.pdx.edu
	Wed Mar 20 13:24:40 2013  - INFO: Checking volume groups
	Wed Mar 20 13:24:40 2013 STEP 2/6 Check peer consistency
	Wed Mar 20 13:24:40 2013  - INFO: Checking disk/0 consistency on node rapier.cat.pdx.edu
	Wed Mar 20 13:24:40 2013 STEP 3/6 Allocate new storage
	Wed Mar 20 13:24:40 2013  - INFO: Adding new local storage on claymore.cat.pdx.edu for disk/0
	Wed Mar 20 13:24:44 2013 STEP 4/6 Changing drbd configuration
	Wed Mar 20 13:24:44 2013  - INFO: activating a new drbd on claymore.cat.pdx.edu for disk/0
	Wed Mar 20 13:24:48 2013  - INFO: Shutting down drbd for disk/0 on old node
	Wed Mar 20 13:24:48 2013  - INFO: Detaching primary drbds from the network (=> standalone)
	Wed Mar 20 13:24:49 2013  - INFO: Updating instance configuration
	Wed Mar 20 13:24:49 2013  - INFO: Attaching primary drbds to new secondary (standalone => connected)
	Wed Mar 20 13:24:50 2013 STEP 5/6 Sync devices
	Wed Mar 20 13:24:50 2013  - INFO: Waiting for instance yermom.cat.pdx.edu to sync disks.
	Wed Mar 20 13:24:55 2013  - INFO: - device disk/0:  0.50% done, 13m 34s remaining (estimated)
	Wed Mar 20 13:26:00 2013  - INFO: - device disk/0:  6.90% done, 15m 53s remaining (estimated)
	Wed Mar 20 13:27:07 2013  - INFO: - device disk/0: 13.40% done, 14m 42s remaining (estimated)
	Wed Mar 20 13:28:26 2013  - INFO: - device disk/0: 21.00% done, 13m 1s remaining (estimated)
	Wed Mar 20 13:29:30 2013  - INFO: - device disk/0: 27.00% done, 14m 32s remaining (estimated)
	Wed Mar 20 13:30:35 2013  - INFO: - device disk/0: 33.20% done, 11m 27s remaining (estimated)
	Wed Mar 20 13:31:40 2013  - INFO: - device disk/0: 39.50% done, 9m 56s remaining (estimated)
	Wed Mar 20 13:32:44 2013  - INFO: - device disk/0: 45.80% done, 9m 20s remaining (estimated)
	Wed Mar 20 13:32:44 2013  - INFO: - device disk/0: 45.80% done, 9m 20s remaining (estimated)
	Wed Mar 20 13:33:49 2013  - INFO: - device disk/0: 52.10% done, 8m 2s remaining (estimated)
	Wed Mar 20 13:34:54 2013  - INFO: - device disk/0: 58.30% done, 6m 54s remaining (estimated)
	Wed Mar 20 13:35:58 2013  - INFO: - device disk/0: 64.60% done, 5m 48s remaining (estimated)
	Wed Mar 20 13:37:03 2013  - INFO: - device disk/0: 70.90% done, 4m 52s remaining (estimated)
	Wed Mar 20 13:38:08 2013  - INFO: - device disk/0: 77.20% done, 3m 50s remaining (estimated)
	Wed Mar 20 13:39:15 2013  - INFO: - device disk/0: 83.70% done, 2m 33s remaining (estimated)
	Wed Mar 20 13:40:20 2013  - INFO: - device disk/0: 90.00% done, 1m 44s remaining (estimated)
	Wed Mar 20 13:41:25 2013  - INFO: - device disk/0: 96.30% done, 37s remaining (estimated)
	Wed Mar 20 13:42:04 2013  - INFO: Instance yermom.cat.pdx.edu's disks are in sync.
	Wed Mar 20 13:42:04 2013 STEP 6/6 Removing old storage
	Wed Mar 20 13:42:04 2013  - INFO: Remove logical volumes for 0

Sometimes you may get an lvm error that looks like this:

	Wed Mar 20 13:15:18 2013  - WARNING: Can't remove old LV: Can't lvremove: exited with exit code 5 -   Unable to deactivate open ganeti-9bc9b089--59f3-
	-4512--9a09--e7f756caadbe.disk0_meta (252:7)\n  Unable to deactivate logical volume "9bc9b089-59f3-4512-9a09-e7f756caadbe.disk0_meta"\n
	Wed Mar 20 13:15:18 2013       Hint: remove unused LVs manually

If this happens you can manually remove the old volume with the lvremove command

    # Log into the node
    ssh katana.cat.pdx.edu
    sudo lvremove 9bc9b089-59f3-4512-9a09-e7f756caadbe.disk0_meta

Mark the node offline
-----------------------

The last step is to mark the node offline

    sudo gnt-node modify -O yes katana.cat.pdx.edu


gnt-cluster verify should now display that one node is offline

	gnt-cluster verify 
	[..]
	Sat Mar 23 14:18:14 2013 * Other Notes
	Sat Mar 23 14:18:14 2013   - NOTICE: 1 offline node(s) found.
	[..]

And that is it, you can now take the node offline for diagnostics or to wait for new parts.

Rebalance the cluster
---------------------

At this point you probably want to rebalance your Ganeti cluser. The following blog post by Lance Albertson does a pretty good job at explaining this process.

http://www.lancealbertson.com/2011/05/rebalancing-ganeti-clusters/
