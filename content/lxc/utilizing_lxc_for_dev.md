Title: Creating a Puppet development environment with LXC
Date: 2013-05-26 16:00
Tags: lxc, puppet
Category: lxc
Slug: puppet-dev-with-lxc
Author: William Van Hevelingen
Summary: Creating a Puppet development environement with LXC


This blog post is about my development setup on my laptop for testing out new software. You will learn how you can easily create LXC containers and connect them to a puppet master in about 20 minutes using the awesome cloning features of LXC.

LXC is a lightweight container virtualization technology very similar to Solaris zones and FreeBSD jails and is availible on most Linux distributions. To learn more and read the docs check out the links at the bottom of the post. 

The first step is to install it.

Install LXC
-----------

On Ubuntu installing LXC is easy and the package comes with working Ubuntu and Debian templates.

    sudo apt-get install lxc


Create a puppet master
----------------------

The first thing we need is a puppet master. To do this we are going to use the lxc-create command to create a minimal Ubuntu Precise instance.

    # Create a fresh precise minimal install
    lxc-create -n pdxpuppet-master -t ubuntu -- --release=precise

    # Start your puppet master
    lxc-start -n pdxpuppet-master -d

    # Determine the ip address
    lxc-ls --fancy

    # Log in with the default username: ubuntu and password: ubuntu
    ssh ubuntu@10.0.3.118

You may need to wait a few seconds for the container to start before the ip address will be displayed in the output of lxc-ls --fancy

Configure your puppet master
----------------------------

Now we need to configure our new instance to be a puppet master.


     # Become the root user
     sudo -i

     # Install wget
     apt-get install wget

     # Install the puppetlabs apt repository
     wget http://apt.puppetlabs.com/puppetlabs-release-precise.deb
     dpkg -i puppetlabs-release-precise.deb
     apt-get update

     # Install the webrick puppetmaster
     apt-get install puppet puppetmaster

The webrick puppetmaster is not recommended for production use. At this point you can choose to configure Apache and [Passenger](http://docs.puppetlabs.com/guides/passenger.html) or an alternative.

Create a puppet client
----------------------

Next we need a puppet client. The process will be almost identical to creating our puppet master.

    # Create a fresh precise minimal install
    lxc-create -n pdxpuppet-client0 -t ubuntu -- --release=precise

    # Start your puppet client0
    lxc-start -n pdxpuppet-client0 -d

    # Determine the ip address
    lxc-ls --fancy

    # Log in with the default username: ubuntu and password: ubuntu
    ssh ubuntu@10.0.3.119

Configure the client
-------------------

Next we need to configure our client to know about the puppet master.

Replace 10.0.3.118 with the ip of your puppetmaster


    # Become the root user
    sudo -i

    # In this environment we don't have DNS so add the puppet master to /etc/hosts
    echo "10.0.3.118 puppet puppet.lan" >> /etc/hosts

    # Install puppet
    apt-get install puppet

    # Make puppet start on boot
    /bin/sed -i 's/START\=no/START\=yes/' '/etc/default/puppet'


At this stage you can add any other useful tools or configuration. I usually install vim, git and ssh keys for root login from my laptop.


After you're finished configuring the client turn it off.

    lxc-stop -n pdxpuppet-client0


Configure Puppet Autosigning on your master
-------------------------------------------

This next step is for convenience. If you want to avoid signing certs in your development environment you can turn on auto signing.

    # On your puppetmaster

    # Allow hosts with domain name lan
    echo "*.lan" >> /etc/puppet/autosign.conf

    # Restart the puppet master
    service puppetmaster restart

Auto signing is described in the docs [here](http://docs.puppetlabs.com/guides/configuring.html#autosignconf)

There are security concerns with auto signing as described in the docs.

    "As any host can provide any certname, autosigning should only be used with great care, and only in situations where you essentially trust any computer able to connect to the puppet master."

In this case my LXC environment is only on my laptop so I'm choosing to enable autosigining.


Add a node definition to your site.pp 
-------------------------------------

Now we need to make a node definition for our client. By using a regex we can allow client 0 through client 9 to connect.

On your puppet master add the following to your site.pp

    # /etc/puppet/manifests/site.pp
    node /pdxpuppet-client[0-9]/ {

      # add code here
    }


Clone more clients using client0
---------------------------------

Now we X more clients. For now we will create 5 more.

    # LXC will make an exact copy and tweak the network configs
    for i in 1 2 3 4 5; do lxc-clone -o pdxpuppet-client0 -n pdxpuppet-client$i ; done

    # Start your new machines
    for i in 1 2 3 4 5; do lxc-start -n pdxpuppet-client$i ; done

After you're clients boot they should automatically check in with the puppetmaster and request certs.


Summary
-------

At this point you have successfully configured a puppet master and five puppet clients that are ready for testing out new code. If you need more clients you can clone pdxpuppet-client0 and generate as many as you need and they will automatically connect to the puppet master on boot.

Resources
---------

* [http://en.wikipedia.org/wiki/LXC](http://en.wikipedia.org/wiki/LXC)

* [http://lxc.sourceforge.net/](http://lxc.sourceforge.net/)

* [https://help.ubuntu.com/12.04/serverguide/lxc.html](https://help.ubuntu.com/12.04/serverguide/lxc.html)
