# MapIt - import postcode and boundary data

## Introduction

[MapIt](https://github.com/alphagov/mapit) is a product of
[MySociety](https://mysociety.org) which we use within GOV.UK to allow
people to enter their postcode and be pointed to their local services.

It is composed of broadly 2 things:

1.  A database of postcodes and the location of their geographical
    centre
2.  A database of administrative entities (e.g. local councils) and
    their boundaries on a map

When a user enters a postcode on GOV.UK, MapIt will look it up to find
the geographical centre and then return information about the
administrative entities that postcode belongs to. We then use this
information to refer the user to local services provided by those
entities.


## Updating Datasets

Datasets for boundary lines are published twice a year (in May and
October) and postcodes are released four times a year (in February, May,
August and November). This means over time our database will become more
and more out of date and users will start to complain. When they do (or
before if possible) we should update the data.

To update a live mapit server we:

1.  [Generate a new database locally](#generate-a-new-database)
2.  [Export the new database to Amazon S3](#export-new-database-to-s3)
3.  [Update servers with the new database](#update-servers-with-new-database)

### 1. Generate a new database

#### <a name="installation">1.1 Prepare your Mapit installation</a>

Checkout the [mapit](https://github.com/alphagov/mapit),
[mapit-scripts](https://github.com/alphagov/mapit-scripts) and
[govuk-docker](https://github.com/alphagov/govuk-docker) repos.

Prepare your Mapit installation in Docker by:
  1.  Running `make mapit` in the `govuk-docker` repo - this will build the image
      and install all the dependencies.
  2.  Reset the database by running `govuk-docker run mapit-app ./reset-db.sh`
      in the `mapit` repo (you can skip this step if you haven't run Mapit locally
      before) - this will drop any existing database, create a new empty one
      and migrate it to the empty schema. See the [Troubleshooting](#troubleshooting)
      section if you have issues.
  3.  Start your Docker container by running `govuk-docker up mapit-app`, and
      check you are able to access `mapit.dev.gov.uk` - it is expected that the
      frontend looks somewhat "broken", that's okay - we only need to worry about
      the database for importing data.


#### <a name="download-latest-data">1.2 Download the latest data from sources</a>

This consists of the [Office for National Statistics Postcode Database (ONSPD)](https://geoportal.statistics.gov.uk/search?collection=Dataset&q=ONS%20Postcode%20Directory), [Ordnance Survey Boundary Line (BL)](https://osdatahub.os.uk/downloads/open/BoundaryLine), and [Ordnance Survey of Northern Ireland (OSNI)](http://osni.spatial-ni.opendata.arcgis.com/) datasets.

> MySociety may have mirrored the latest datasets on their cache server: <http://parlvid.mysociety.org/os/> so check there first.

  1. **ONS Postcode Database** - ONSPD releases can be found via the Office
      for National Statistics (ONS) at
      <http://geoportal.statistics.gov.uk/datasets?q=ONS+Postcode+Directory+(ONSPD)&sort_by=name&sort_order=asc>
      or via
      <http://geoportal.statistics.gov.uk/> and selecting the latest ONSPD
      from the Postcodes product drop down.
  2.  **Boundary Line data** - BL releases can be found via the Ordnance Survey (OS)
      at
      <https://osdatahub.os.uk/downloads/open/BoundaryLine> and select the
      `ESRI Shapefile` format to download
  3.  **ONSI data** - For the ONSI data we now point to Mysociety's URL in the
      [check-onsi-downloads](https://github.com/alphagov/mapit-scripts/blob/master/check-osni-downloads#L18) script, as there have not been any changes since December 2015.
      It's still worth checking if there are any updates. See [about datasets](/ABOUT-DATASETS.md) for more information.


#### <a name="upload-latest-data">1.3 Upload the latest data to Amazon S3</a>

Upload the latest ONS Postcode Database, Boundary Line, and OSNI datasets
to the `govuk-custom-formats-mapit-storage-production` S3 bucket. The path
should be of the format `source-data/<year-month>/<filename>`. Also ensure
that you have set the permissions for the datasets to be `public` so that
when you run the scripts later they are able to access the S3 files.

>**Note:** the uploaded `<filename>` must match the naming convention
of the dataset files. This may not be case when initially downloaded.
For example, the ONSPD download for November 2018 is `2018-11`.
Files within `2018-11/data` are named `ONSPD_NOV_2018_UK.xxx`.
Before uploading in S3, rename folder `2018-11` to `ONSPD_NOV_2018_UK`.


#### <a name="update-url-paths">1.4 Update URL paths in data import scripts</a>

Update the [import-uk-onspd](https://github.com/alphagov/mapit-scripts/blob/master/import-uk-onspd)
script in `mapit-scripts` to refer to the URLs of the new releases uploaded to
S3 in the [last step](#upload-latest-data).

**Note:** If the ONSI data has been updated and uploaded to S3 update the
[check-onsi-downloads](https://github.com/alphagov/mapit-scripts/blob/master/check-osni-downloads#L18) script to refer to the new S3 URL.


#### <a name="run-import-script">1.5 Start running the import script</a>

In your Mapit directory run the `import-uk-onspd` script to import the data using Docker:

    $ govuk-docker run mapit-app ../mapit-scripts/import-uk-onspd

>This is a long process, it's importing 1000s of boundary objects and
\~2.6 million postcodes, and **takes at least 4.5 hours to run**. The first hour is
particularly important to monitor as this is when it has typically failed
in the past.

If the scripts fail you'll have to investigate why and possibly
update it to change how we import the data.

Some suggestions of places to look for help:
- [Mysociety's documentation](https://mapit.mysociety.org/docs/)
- [Mapit's logged issues](https://github.com/mysociety/mapit/issues)

Also see the [Troubleshooting](#troubleshooting) section for past issues.

If you do have to fix the import scripts, or create new ones, consider
talking with Mysociety developers to see if they're aware and if you can push
those changes back upstream.

> **Note:** If the script fails, you'll need to drop and recreate
the database by running the `reset-db.sh` script and then run `import-uk-onspd`
again. If you have database issues see the [troubleshooting](#troubleshooting)
section.


#### <a name="check-missing-codes">1.6 Check for missing codes</a>

The ONS used to identify areas with SNAC codes (called ONS
in mapit). They stopped doing this in 2011 and started using GSS
codes instead. New areas will not receive SNAC codes, and (for the
moment at least) much of GOV.UK relies on SNAC codes to link
things up, for example [Frontend's AuthorityLookup](https://github.com/alphagov/frontend/blob/master/lib/authority_lookup.rb).

The `import-uk-onspd` script's last action is to run a script to show missing codes.
It's the line that reads

    $MANAGE mapit_UK_show_missing_codes

This iterates over all area types we care about and lists those that
are missing a GSS code (hopefully none) and how many are missing an
ONS/SNAC code. If it lists any areas that are missing codes and you
don't expect them (run the script on production or integration if
you're not sure) you'll need to investigate.

Ssh into one of the machines and run:

    $ cd /var/apps/mapit
    $ sudo -u deploy govuk_setenv mapit venv3/bin/python manage.py mapit_UK_show_missing_codes

Then compare the output with that generated in your local Docker container.

An example of the output (May 2019 data):

        Show missing codes

        11874 areas in current generation (1)

        Checking ['EUR', 'CTY', 'DIS', 'LBO', 'LGD', 'MTD', 'UTA', 'COI'] for missing ['ons', 'gss', 'govuk_slug']
        12 EUR areas in current generation
        2 EUR areas have no ons code:
        Northern Ireland 11874 (gen 1-1) Northern Ireland
        Scotland 9199 (gen 1-1) Scotland
        26 CTY areas in current generation
        192 DIS areas in current generation
        33 LBO areas in current generation
        11 LGD areas in current generation
        36 MTD areas in current generation
        109 UTA areas in current generation
        1 COI areas in current generation

There is a also script in mapit
[mapit_gb/management/commands/mapit_UK_add_missing_codes.py](https://github.com/alphagov/mapit/blob/master/mapit_gb/management/commands/mapit_UK_add_missing_codes.py) that
you can update to add the codes once you work out if anything can
be done. See [this example](https://github.com/alphagov/mapit/commit/532f3e88ce0f5dea64b8f7eede6fb80605648e21).

Once these have been updated, the API will return the new GSS code, albeit mislabelled as an ONS code.

**Note** [Licensify](https://github.com/alphagov/licensify) also depends on knowledge of SNAC codes to build it's own API paths. It will be necessary to update this [file](https://github.com/alphagov/licensify/blob/master/common/app/uk/gov/gds/licensing/model/SnacCodes.scala) with the new GSS codes and corresponding area.


#### <a name="test-postcodes">1.7 Test some postcodes</a>

If you've had users complaining that their postcode isn't
recognised, then try _those_ postcodes and any other ones
you know. If you don't know any postcodes, try this random one:

    $ curl http://mapit.dev.gov.uk/postcode/ME206QZ

You should expect a `200` response with data present in the `areas`
field of the response. See [this example output](https://github.com/alphagov/mapit/commit/532f3e88ce0f5dea64b8f7eede6fb80605648e21) for an idea of what to expect.

You can also compare the response to existing data we have in one of our environments
and on Mysociety.

    $ curl https://mapit.integration.govuk-internal.digital/postcode/ME206QZ
    $ curl https://mapit.mysociety.org/postcode/ME206QZ

>Ensure you test postcodes from **all parts of the UK**, since Northern
Ireland data has been loaded separately.


#### <a name="make-prs">1.8 Make PRs for any changes you had to make</a>

You will have changed the [import-uk-onspd](https://github.com/alphagov/mapit-scripts/blob/master/import-uk-onspd) and [check-onsi-downloads](https://github.com/alphagov/mapit-scripts/blob/master/check-osni-download)
scripts to refer to new datasets. If anything failed you may have had
to change other things in the mapit repo too.


### 2. Export new database to S3

Export the database you just built in your Docker container:

    $ govuk-docker run mapit-app pg_dump -U postgres mapit | gzip > mapit.sql.gz

**It should be \~500Mb in size.** You'll want to give it a name that refers
to what data it contains. Perhaps `mapit-<%b%Y>.sql.gz` (using
`strftime` parlance) for a standard release, or
`mapit-<%b%Y>-<a-description-of-change>.sql.gz` if you've had to change
the data outside the normal dataset releases.

Arrange to have the file you just created uploaded to the
`govuk-custom-formats-mapit-storage-production` S3 bucket, in the same folder
the new data has been uploaded to, and ensure that it's permission is set to `public`.


### 3. Update servers with new database

**NB: THIS REQUIRES ACCESS TO GOV.UK PRODUCTION**

Once the data has been uploaded change the URL and checksum (using
`sha1sum <your-mapit-file.sql.gz>`) reference in `import-db-from-s3.sh`
to refer to your new file. Submit change as a PR against
[Mapit](https://github.com/alphagov/mapit) and deploy following the normal
process.

> **Note: Only deploy this change to production once the new data has been tested
in staging. If a new Mapit machine gets created in AWS, it will automatically
try importing the data.**

Now that your changes have been deployed, you can test the new database in
`AWS staging` before moving to `production`.

Once you have tested that a new mapit node works as expected, you can
update each mapit node in turn using a [fabric
script](https://github.com/alphagov/fabric-scripts/blob/master/mapit.py#L10):

    $ fab $environment -H <ip_address> mapit.update_database_via_app

We can happily survive with one mapit-server in an environment while
this is done.

## Testing a server

We have two expectations for an updated Mapit database:

- [Changes to postcodes](#for-postcodes)
- [Changes to areas](#for-areas)

### Changes to Postcodes

#### Existing postcodes

It returns a `200 OK` status for all postcode requests that
previously returned `200 OK`. The ONSPD is a complete set of all
postcodes, live and terminated and we import the whole thing so
postcodes should never be "deleted". If a request for a postcode
previously succeeded, it should still succeed.

#### Invalid postcodes
It returns either a `404 Not Found` or a `200 OK` for all postcode
requests that previously returned `404 Not Found`. As postcodes are
released every 3 months, people may have searched for one that did
not exist previously that is in our new dataset (now `200 OK`).
However if they searched for a bad postcode, or something that is
not a postcode at all, we would still expect that to
`404 Not Found`.

### Changes to Areas

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

### Generating some test data

The best source of testing data for postcode lookups is Production, so
let's grab all the relevant responses from yesterday's log:

    $ your laptop> ssh <mapit_production_machine>
    $ mapit-1> sudo awk '$9==200 {print "http://localhost:3108" $7}' /var/log/nginx/mapit-access.log.1 >mapit-200s
    $ mapit-1> sudo awk '$9==404 {print "http://localhost:3108" $7}' /var/log/nginx/mapit-access.log.1 >mapit-404s
    $ mapit-1> sudo awk '$9==302 {print "http://localhost:3108" $7}' /var/log/nginx/mapit-access.log.1 >mapit-302s

Download the files via the jumpbox, e.g.

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

### Running the test samples script

For a more comprehensive test, you can use the [test-samples.sh](https://github.com/alphagov/mapit/blob/master/test-samples.sh)
script, which needs to be run before and after a database upgrade:

    $ your laptop> ssh mapit-1.production
    $ mapit-1> /var/apps/mapit/test-samples.sh sample

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

## Troubleshooting

### Unable to drop the database when running the ./reset-db.sh script

1. Log into the database

2. Prevent future connections by running

        $ REVOKE CONNECT ON DATABASE mapit FROM public;
3. Terminate all connections to the database except your own:

        $ SELECT pid, pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = current_database() AND pid <> pg_backend_pid();

Failing that, stop `collectd`, it probably connects again the moment the old connection gets terminated:

    $sudo service collectd stop

### Hitting exceptions where an area has a missing parent or spelt incorrectly

If you see something similar to:

  ```
  get() returned more than one area -- it returned 2!
  ```

  ```
  /var/govuk/mapit/mapit/management/find_parents.py:49
  Exception: Area Moray [9325] (SPC) does not have a parent?
  ```

Compare the entry with the database in `integration` or `staging` to identify what information is missing or needs to be corrected. Searching for the data on https://mapit.mysociety.org might also be helpful.

You can manually fix it by adding a correction in [mapit/management/find_parents.py](https://github.com/alphagov/mapit/blob/master/mapit/management/find_parents.py). See [this example](https://github.com/alphagov/mapit/commit/5b2ede155a157d7d69883a6a0197513bcbcca4bb) for more information.
