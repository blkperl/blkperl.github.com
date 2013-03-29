Title: Replacing a Puppet CA Cert
Date: 2013-03-26 22:50
Tags: puppet, openssl
Category: puppet
Slug: replace-puppet-ca
Author: William Van Hevelingen
Summary: Replacing a Puppet CA cert

This is more of a story than a tutorial and I make no claims that this is the "correct" way to replace a Puppet CA cert but this is how we did it.

Our puppet ca cert was going to expire in about 18 hours so we set aside some time when no one else was working on other systems and madly searched the internet for tidbits of information to replace the cert.

In our environment we have a Puppet CA Server, a puppetmaster, and puppetdb/dashboard server and about 200 nix clients.

Prep Work
---------

* Stop all puppet agents.

If running the daemon, run `service puppet stop` on all the clients

If running by cron then disable all the puppet crons.

This is not necessary but it will prevent the clients from spamming logs while you replace the certs. It may also prevent some clients from getting into a weird limbo state.

* Verify time is correct on all the puppetmasters.

If the servers are not in sync then the certs generated will not work. I would recommend using NTP if you're not already running it.

Generate a new CA Cert
----------------------

On the puppet ca remove the expired cert.

    rm -rf /var/lib/puppet/ssl

Add any alternate dns names to /etc/puppet/puppet.conf

    dns_alt_names=puppetca,puppetca.cat.pdx.edu,zeratul.cat.pdx.edu,zeratul

Review the puppet.conf docs for other CA settings you may want to set before moving on.

Generate a new cert for the CA
------------------------------

    puppet cert --generate zeratul.cat.pdx.edu

Verify the new ca.pem and ca cert look correct.

    openssl x509 -text -noout -in /var/lib/puppet/ssl/certs/ca.pem
    openssl x509 -text -noout -in /var/lib/puppet/ssl/certs/zeratul.cat.pdx.edu.pem

Specifically, the validity field should now be 5 years in the future. You can set the expiration date in puppet.conf before you generate the cert if you want a longer or shorter period.

    $ openssl x509 -text -noout -in /var/lib/puppet/ssl/certs/ca.pem | grep -i validity -A 2
            Validity
                Not Before: Mar 25 03:20:40 2013 GMT
                Not After : Mar 25 03:20:40 2018 GMT

Restart apache.

    service apache2 restart

Generate a new cert for each puppet master
------------------------------------------

    # request a new cert on the puppetmaster
    puppet agent --test --dns_alt_names=tassadar,tassadar.cat.pdx.edu,puppet,puppet.cat.pdx.edu

    # on the ca server sign the cert
    puppet cert --allow-dns-alt-names sign tassadar.cat.pdx.edu

    # restart apache on the puppet master
    service apache2 restart

At this point your puppet master if configured to be an agent of itself, should be able to run `puppet agent --test` with no errors unless you are running puppetdb.

Generate a new cert for puppetdb
--------------------------------

The [official docs](http://docs.puppetlabs.com/puppetdb/1.1/maintain_and_tune.html#redo-ssl-setup-after-changing-certificates) did not work for us. We had to add some additional steps documented below and we filed a [bug](https://projects.puppetlabs.com/issues/19904) to update the docs or fix the `puppetdb-ssl-setup` command.

    # Remove the old puppetdb certs on the puppetdb server
    rm -rf /etc/puppetdb/ssl

    # Generate new puppetdb certs
    puppetdb-ssl-setup

    # restart the service
    service puppetdb restart

    # verify it restarts by watching the log (it may take a few minutes)
    tail -f /var/log/puppetdb/puppetdb.log

At this point if you did everything correct, the puppetmaster should be able to checkin to itself as a client with no errors and be able to download a catalog.

Request a cert for dashboard
----------------------------

Excerpt from the [official docs](http://docs.puppetlabs.com/dashboard/manual/1.2/configuring.html) for the 1.2 stable release of dashboard.

    # on the dashboard server
    cd /usr/share/puppet-dashboard
    rake cert:request

    # on the ca server
    puppet cert sign dashboard

    # restart apache on the dashboard server
    service apache2 restart

Generate new certs for all your clients
---------------------------------------

Note if any clients are offline during the process they will need a new cert generated and signed when they come back online.

We used a bash for loop that looked something like this.

    cat alltheclients.txt | xargs -P 10 -n 1 -I box ssh -4 box 'rm -fr /var/lib/puppet/ssl && puppet agent -t'

The key part in this bash one liner is removing `/var/lib/puppet/ssl` and requesting a new cert.

Then on the puppet ca server we signed the new certs

    # For each client sign the new cert
    puppet cert sign client2.cat.pdx.edu

Or you can use the `--all` flag

 There are some security risks with doing this. Basically for the same reasons on why not to use autosign. Read Brice's [blog](http://www.masterzen.fr/2010/11/14/puppet-ssl-explained/) for more information about Puppet and SSl.

    puppet cert sign --all


Summary
-------

This was a really painful process and is poorly documented. A lot of the clients were left in a broken state and needed to be kicked because the original for loop failed (probably because we didn't turn off the agents first). About 3 hours after we begun we had most of the clients working again and we fixed some stragglers the next day.

If someone has a better/easier process for doing this, please blog about it or submit a pull request to the [official docs](http://docs.puppetlabs.com/contribute.html#editing-the-documentation).

