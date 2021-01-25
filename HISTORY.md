## History of Boundary Line changes

### November 2020 import

Boundary Line (BL) data - October 2020 - [data in S3 bucket](https://s3.console.aws.amazon.com/s3/object/govuk-custom-formats-mapit-storage-production?region=eu-west-1&prefix=source-data/2020-11/bdline_gb-2020-10.zip)

[ONS Postcode (ONSPD) data - November 2020](https://geoportal.statistics.gov.uk/datasets/ons-postcode-directory-november-2020) - [data in S3 bucket](https://s3.console.aws.amazon.com/s3/object/govuk-custom-formats-mapit-storage-production?region=eu-west-1&prefix=source-data/2020-11/ONSPD_NOV_2020_UK.zip)

#### Boundary line changes:
- Aylesbury Vale (E07000004), Chiltern (E07000005), South Bucks (E07000006) and
Wycombe (E07000007) have now been merged with Buckinghamshire council, and their
GSS codes are now inactive.
- Buckinghamshire county (E10000002) is now a unitary authority UTA (E06000060)

As elections have not yet taken place for Buckinghamshire to use its new wards,
the old wards still need to exist, which has been updated and covered in this
[Mysociety issue](https://github.com/mysociety/mapit/issues/365) and [this PR](https://github.com/mysociety/mapit/pull/367)

**We may want to revert some of this code in future once the elections have
taken place, or wait for Mysociety to make the changes and pull them upstream.**

See https://geoportal.statistics.gov.uk/datasets/f7ba20849bc54f58bbb8ef14c640f9a9_0
for more information.
