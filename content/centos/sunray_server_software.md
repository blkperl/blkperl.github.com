Title: Installing Sunray Software Server (SRSS) on Centos 5.x
Date: 2013-05-18 21:35
Tags: centos, sunray, oracle, rhel, redhat
Category: centos
Slug: centos_sunray
Author: William Van Hevelingen
Summary: Installing SunRay Software Server (SRSS) on Centos 5.x

These are the steps I took to get the SunRay software working on Centos. I was able to get this working thanks to scraps of information from [Peter Senna Tschudin's blog](http://blog.parahard.com/2009/06/installing-sunray-ii- erver-software-on.html) In addition to get it working on 32bit like in Peter's blog, I also got it working on 64 bit. These are the instructions for 64bit.

The SunRays we have are the SunRay 2 model updated with the latest firmware.

Download the software from Oracle's support portal (requires login)
-------------------------------------------------------------------

    cd /opt/
    # download files from Oracle's website
    unzip V37034-01.zip
    unzip p16406547_111_Generic.zip

Install the dependencies
------------------------

    yum install glib dhcp openldap-clients tftp-server libXp libXfont.i386 openmotif22 openssl compat-libstdc++-33 libusb-devel compat-openldap kernel-devel gdbm.i386 gcc openmotif.i386 sssd-client.i386

If you are not using sssd you will need to install the nscd.i386 package.


Install the firmware
--------------------

    cd /opt/sros_11.1.1.0/
    ./utfwinstall 
    Installing Sun Ray Operating Software 11.1.1.0

    Sun Ray Operating Software 11.1.1.0 has been successfully installed.

    This output has been logged to

        /var/log/utfwinstall.2013_05_09_14:48:54.log

    +++ Done.

Install the bundled JRE and Apache Tomcat
-----------------------------------------

    cd /opt/srs_5.4.0.0-Linux.i386/Supplemental/Java_Runtime_Environment/Linux
    sh jre-6u41-linux-i586.bin 
    mv jre1.6.0_41/ /opt/
    cd /opt/srs_5.4.0.0-Linux.i386/Supplemental/Apache_Tomcat
    gunzip apache-tomcat-5.5.36.tar.gz
    tar xvf apache-tomcat-5.5.36.tar 
    mv apache-tomcat-5.5.36 /opt/
    ln -s /opt/apache-tomcat-5.5.36/ /opt/apache-tomcat

Install the Sunray Server Software
---------------------------

    cd /opt/srs_5.4.0.0-Linux.i386
    ./utsetup

    [...]
    Accept? (Y/N) y
    [...]
    Enter Java v1.6 (or later) location: [/usr/java] /opt/jre1.6.0_41/
    [...]
    Continue? (Y/N) [Y] y

    Enter new UT admin password:  
    Again: Enter new UT admin password:  
    Configure Sun Ray Web Administration? (Y/N) [N] y

    Enter Apache Tomcat installation directory [/opt/apache-tomcat] 

    Enter HTTP port number [1660] 8080

    Enable secure connections? (Y/N) [Y] y

    Enter HTTPS port number [1661] 8081

    Enter Tomcat process username [utwww] 

    Enable remote server administration? (Y/N) [N] Y

    Configure Sun Ray Kiosk Mode? (Y/N) [N] N

    Configure this server for a failover group? (Y/N) [N] 

    About to configure the following software products:

    Sun Ray Data Store 3.5
        Hostname: mysunrayserver.example.org
        Sun Ray root entry: o=utdata
        Sun Ray root name: utdata
        Sun Ray utdata admin password: (not shown)
        SRDS 'rootdn': cn=admin,o=utdata

    Sun Ray Web Administration hosted at Apache Tomcat/5.5.36
        Apache Tomcat installation directory: /opt/apache-tomcat
        HTTP port number: 8080
        HTTPS port number: 8081
        Tomcat process username: utwww
        Remote server administration: Enabled

    Sun Ray Server Software 4.5
        Failover group: no
        Sun Ray Kiosk Mode: no
    Continue? (Y/N) [Y]

    Enter groupname for Windows Connector [utwc] 

    Enter group ID (gid) for the group [auto] 

    Do you want to configure Firmware downloads for Sun Ray clients? (Y/N) [Y] 

Reboot
------

Seriously you should reboot


If the services are not running on reboot
-----------------------------------------

You can manually start them with:

    /opt/SUNWut/sbin/utadm -L on
    /opt/SUNWut/sbin/utstart

SunRay Web Administration
-------------------------

Log into [https://mysunrayserver.example.org:8081](https://mysunrayserver.example.org:8081)

With the user: admin and the password you specified in the installer.

Note: Replace port 8081 with the port you selected in the installer if you did not select 8081.

If you can't log in because the "data store is not responding" proceed to the debugging section.


* Click "Advanced"
* Check all the encryption buttons
* Switch soft to hard for client and server
* Following instruction to restart client


Debugging
---------

The following two log files were especially helpful in debugging problems.

    tail -f /var/opt/SUNWut/log/messages
    tail -f /var/log/autholog

Security
--------

We have the SunRays in there own vlan and only the SunRay servers are allowed to communicate with them. You should also firewall the Web Admin ports in my case port 8080 and 8081.

Summary
-------

I havn't had a lot of luck with a consistent installation using the instructions above. If it doesn't work the first time try uninstalling and resintalling the SunRay software. Also I was doing this with SELinux disabled and we already had working SunRays with Solaris 10 so I can't really comment on the dhcp configs or any special network acls we may have in place.
