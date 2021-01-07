# This script is for a one off import of govuk slugs for local authorities

import csv
import os.path

from django.core.management.base import BaseCommand
from mapit.models import Area, NameType


class Command(BaseCommand):
    help = 'Imports local authority names from openregister'

    def handle(self, *args, **options):
        name_type = NameType.objects.get(code='M')

        iso_to_gss = {}

        iso_to_gss_tsv = csv.reader(open(os.path.dirname(__file__) + '/../../data/openregister_gss_to_iso3166_mapping.tsv'), delimiter='\t')
        next(iso_to_gss_tsv)  # header line

        for gss, local_authority, name in iso_to_gss_tsv:
            iso_to_gss[local_authority] = gss

        local_authorities_tsv = csv.reader(open(os.path.dirname(__file__) + '/../../data/openregister_local_authorities.tsv'), delimiter='\t')
        next(local_authorities_tsv)  # header line

        for iso_code, country_code, local_authority_type, parent_local_authority, name, name_cy, official_name, website, start_date, end_date in local_authorities_tsv:

            gss_code = iso_to_gss[iso_code]

            if gss_code:
                try:
                    area = Area.objects.get(codes__code=gss_code, codes__type__code='gss')
                    area.names.update_or_create(type=name_type, defaults={'name': official_name})

                except Area.DoesNotExist:
                    # An area that existed at the time of the mapping, but no longer

                    # List of known authorities that no longer exist or have been
                    # merged with another
                    merged_authorities = {
                        'Bournemouth Borough Council': 'E06000028',
                        'Borough of Poole': 'E06000029',
                        'Dorset County Council': 'E10000009',
                        'Christchurch Borough Council': 'E07000048',
                        'East Dorset District Council': 'E07000049',
                        'North Dorset District Council': 'E07000050',
                        'Purbeck District Council': 'E07000051',
                        'West Dorset District Council': 'E07000052',
                        'Weymouth and Portland Borough Council': 'E07000053',
                        'Dorset County Council': 'E10000009',
                        'Forest Heath District Council': 'E07000201',
                        'St Edmundsbury Borough Council': 'E07000204',
                        'Suffolk Coastal District Council': 'E07000205',
                        'Waveney District Council': 'E07000206',
                        'Taunton Deane Borough Council': 'E07000190',
                        'West Somerset Council': 'E07000191',
                        'Fife Council': 'S12000015',
                        'Glasgow City Council': 'S12000046',
                        'North Lanarkshire Council': 'S12000044',
                        'Perth and Kinross Council': 'S12000024',
                        'Buckinghamshire County Council': 'E06000060'
                    }

                    if official_name not in merged_authorities and gss_code not in merged_authorities:
                        print ('Area for {authority} {gss_code} not found'.format(
                            authority=official_name,
                            gss_code=gss_code
                        ))
