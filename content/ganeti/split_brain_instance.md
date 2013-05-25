Title: Fixing a split brain Ganeti instance
Date: 2013-05-24 23:08
Tags: ganeti, kvm, drbd
Category: ganeti
Slug: split-brain-ganeti
Author: William Van Hevelingen
Summary: Fixing a split brain Ganeti instance

Recovering from split brain
---------------------------

We run a 4 node Ganeti cluster and during a failover of a node some instances got degraded disks. We're not sure how it happened but some quick googling told us it was a split brain and is recoverable. The following is how we confirmed it was split brain and how we repaired the affected instances.

You can identify a split brain by the following.
------------------------------------------------

Degraded disks in gnt-instance info

    on primary:   /dev/drbd1 (147:1) in sync, status *DEGRADED*
    on secondary: /dev/drbd9 (147:9) in sync, status *DEGRADED*

StandAlone state on the primary (/proc/drbd)

     1: cs:StandAlone ro:Primary/Unknown ds:UpToDate/DUnknown   r-----
        ns:969536 nr:0 dw:22564060 dr:43036016 al:242 bm:2652 lo:0 pe:0 ua:0 ap:0 ep:1 wo:f oos:254024

StandAlone state on the secondary (/proc/drbd)

    9: cs:StandAlone ro:Primary/Unknown ds:UpToDate/DUnknown   r-----
        ns:0 nr:969536 dw:24185104 dr:996 al:0 bm:1293 lo:0 pe:0 ua:0 ap:0 ep:1 wo:f oos:0

Steps to repair
===============

Recreate the secondary
----------------------

(assuming you think the primary is healthy)

    # replace $another_node with any node that is not the primary or secondary
    gnt-instance replace-disks -n  $another_node pika.cat.pdx.edu

Wait for disks to re-sync
------------------------

You can watch the progress by looking at /proc/drbd

    1: cs:SyncSource ro:Primary/Secondary ds:UpToDate/Inconsistent C r-----
        ns:16437312 nr:0 dw:22602340 dr:59475304 al:256 bm:3653 lo:1 pe:123 ua:64 ap:0 ep:1 wo:f oos:4555336
            [==============>.....] sync'ed: 78.3% (4448/20480)Mfinish: 0:01:14 speed: 61,144 (58,212) K/sec

Verify the disks now
----------------

    dirk:~# gnt-instance info $instance | grep drbd
      Disk template: drbd
        - disk/0: drbd8, size 20.0G
          on primary:   /dev/drbd1 (147:1) in sync, status ok
          on secondary: /dev/drbd1 (147:1) in sync, status ok



