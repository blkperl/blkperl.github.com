Title: Removing a patch from Solaris 10
Date: 2013-03-27 12:00
Tags: solaris
Category: solaris
Slug: remove_solaris_patch
Author: William Van Hevelingen
Summary: How to remove a patch on Solaris 10

In this example we removed a custom IDR patch provided by Oracle.

Check to see if the patch is installed
--------------------------------------

    :::bash
    caerbannog# showrev -p | grep 148363
    Patch: IDR148363-26 Obsoletes:  Requires: 147441-26 Incompatibles: 147441-27 Packages: SUNWnfsckr, SUNWzfskr, SUNWzfsu, SUNWzfsr

Remove the patch with patchrm
-----------------------------

    :::bash
    caerbannog# patchrm IDR148363-26
    Validating patches...

    Loading patches installed on the system...

    Done!

    Checking patches that you specified for removal.

    Done!

    Approved patches will be removed in this order:

    IDR148363-26
    Preparing checklist for non-global zone check...

    Checking non-global zones...


    This patch passes non-global zone check.
    IDR148363-26


    Summary for zones:

    Zone crisco

    Rejected patches:
    None.
    tches that passed the dependency check:
    None.


    Removing patches from non-global zones

    Removing patches from zone crisco
    Removing patch IDR148363-26...
    Done!

    Checking installed patches...

    Backing out patch IDR148363-26...

    Patch IDR148363-26 has been backed out.


    Removing patches from zone nt4

    Removing patches from zone sfw

    Removing patches from global zone
    Removing patch IDR148363-26...

    Checking installed patches...

    Executing prebackout script...
    Backing out patch IDR148363-26...

    Executing postbackout script...
    Patch IDR148363-26 has been backed out.

    Done!


