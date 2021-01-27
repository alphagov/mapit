# Testing a server with an updated Mapit database

We have two expectations for an updated Mapit database:

- [Changes to postcodes](#changes-to-postcodes)
- [Changes to areas](#changes-to-areas)

## Changes to Postcodes

### Existing postcodes

It returns a `200 OK` status for all postcode requests that
previously returned `200 OK`. The ONSPD is a complete set of all
postcodes, live and terminated and we import the whole thing so
postcodes should never be "deleted". If a request for a postcode
previously succeeded, it should still succeed.

### Invalid postcodes
It returns either a `404 Not Found` or a `200 OK` for all postcode
requests that previously returned `404 Not Found`. As postcodes are
released every 3 months, people may have searched for one that did
not exist previously that is in our new dataset (now `200 OK`).
However if they searched for a bad postcode, or something that is
not a postcode at all, we would still expect that to
`404 Not Found`.

## Changes to Areas

A url of the form `/area/<ons-or-gss-code` will result in a
`302 Redirect` to a url `/area/<internal-id>`.

As part of the import process it's quite likely that the internal ids
will have changed. We should therefore check that all `302 Redirect`
request still result in a `302 Redirect`, and that what it redirects to
is a `200 OK`. It means we can't really expect all `200 OK` messages
regardless of the URL to remain `200 OK` - because the import will
change ids.

You can test the new database using one of the options:
1. [Generating some test data](#generating-some-test-data)
2. [Running the test samples script](#running-the-test-samples-script)

## Generating some test data

The best source of testing data for postcode lookups is Production, so
let's grab all the relevant responses from yesterday's log:

    $ your laptop> ssh <mapit_production_machine>
    $ mapit-1> sudo awk '$9==200 {print "http://localhost:3108" $7}' /var/log/nginx/mapit-access.log | sort | uniq >mapit-200s
    $ mapit-1> sudo awk '$9==404 {print "http://localhost:3108" $7}' /var/log/nginx/mapit-access.log | sort | uniq >mapit-404s
    $ mapit-1> sudo awk '$9==302 {print "http://localhost:3108" $7}' /var/log/nginx/mapit-access.log | sort | uniq >mapit-302s

> In the commands above, for every line where the 9th field is ‘200’, print the string “http://localhost:3108” followed by the 7th field of that line, which is the postcode.

Download the files via the jumpbox and store in your /Downloads folder, e.g.

    $ scp -r -oProxyJump=jumpbox.production.govuk.digital <ip_address>:mapit-200s ~/Downloads/

Then copy the three files (mapit-200s, mapit-404s, mapit-302s) to the server you're testing on, e.g.

    $ scp -v -r -oProxyJump=jumpbox.staging.govuk.digital ~/Downloads/mapit-302s <ip_address>:~

In the server you want to test run the following:

1. Test that all the 200s are still 200s:

        $ while read line; do curl -sI $line | grep HTTP/1.1 ; done <mapit-200s | sort | uniq -c
          27916 HTTP/1.1 200 OK
2. Test that all the old 404s are either 200s or 404s:

        $ while read line; do curl -sI $line | grep HTTP/1.1 ; done <mapit-404s | sort | uniq -c
          104 HTTP/1.1 200 OK
          331 HTTP/1.1 404 Not Found
3. Test that all the 302s are still 302s:

        $ while read line; do curl -sI $line | grep HTTP/1.1 ; done <mapit-302s | sort | uniq -c
          807 HTTP/1.1 302 Found
4. Check that the 200s are still returning areas:

        $ while read line; do curl $line | python -c "import sys, json; data = json.load(sys.stdin); print '${line} found' if len(data['areas']) > 0 else '${line} missing'"; done <mapit-200s

>**Note**: Checking the 200's can take around 30 minutes. You can also see the CPU and load on this [Grafana graph](https://grafana.blue.production.govuk.digital/dashboard/file/machine.json?refresh=1m&orgId=1) and select the machine.

This process has been automated somewhat via the following [fabric
script](https://github.com/alphagov/fabric-scripts/blob/master/mapit.py#L51):

    $ fab $environment -H <ip_address> mapit.check_database_upgrade

**Note**: This replays yesterday's traffic from the machine you
run it on rather than replaying traffic from production. Useful when
upgrading production environments, perhaps less so for upgrading other
environments.

## Running the test samples script

For a more comprehensive test, you can use the [test-samples.sh](https://github.com/alphagov/mapit/blob/master/test-samples.sh)
script, which needs to be run before and after a database upgrade:

    $ your laptop> ssh mapit-1.production
    $ mapit-1> sudo su - root /var/apps/mapit/test-samples.sh sample

> This can take around 15-20 minutes

Perform the database import in the usual way, and then run the script
in "check" mode, to download the postcode data again and diff the
results:

    $ your laptop> ssh mapit-1.production
    $ mapit-1> /var/apps/mapit/test-samples.sh check

Once you have tested the updated mapit node works as expected, you can update
the other mapit nodes, and then the same on production.

## Things you might have to fix

The Office for National Statistics maintains a series of codes that represent a
wide range of geographical areas of the UK. MapIt includes these and they are
unique to each area, but an area can change code, for example when boundaries
change. If this happens, you might have to change some of our apps to use the
new codes instead of the old ones.

Our forked repo of MapIt contains a file [``mapit_gb/data/authorities.json``]
(https://github.com/alphagov/mapit/blob/master/mapit_gb/data/authorities.json)
which contains a list of Local Authorities, their slugs and their GSS codes.
During the import (invoked by the `import-uk-onspd` script), the GSS codes are
used to match to the areas in MapIt that represent LocalAuthorities and the
slugs are added to each of the areas. These GSS codes need to be kept up to date
in case they change. An example of doing this is [frontend PR 948]
(https://github.com/alphagov/frontend/pull/948) (when the file was still
residing in Frontend,[it has been moved it to MapIt since]
(https://github.com/alphagov/mapit/pull/20)).
