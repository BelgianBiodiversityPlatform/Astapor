import csv

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point

from specimens.models import Person, SpecimenLocation, Specimen

# TODO: document use of this script:
# - export Google Sheet (specimens) as CSV (separator: comma)
# - Column name is important, not column order
# - Lat/lon use comma as a separator

class Command(BaseCommand):
    help = 'Initial data import to populate the tables'

    def add_arguments(self, parser):
        parser.add_argument('csv_file')

        parser.add_argument(
            '--truncate',
            action='store_true',
            dest='truncate',
            default=False,
            help='Truncate specimens (and related) tables prior to import',
        )

    def handle(self, *args, **options):
        self.stdout.write('Importing data from file...')
        with open(options['csv_file']) as csv_file:
            if options['truncate']:
                self.stdout.write('Truncate existing data...', ending='')
                Person.objects.all().delete()
                SpecimenLocation.objects.all().delete()
                Specimen.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('OK'))

            for i, row in enumerate(csv.DictReader(csv_file, delimiter=',')):
                self.stdout.write('Processing row #{i}...'.format(i=i), ending='')
                # Identificators
                id_first_name, id_last_name = row['Identified_by'].split()
                identificator, _ = Person.objects.get_or_create(first_name=id_first_name, last_name=id_last_name)

                # Specimen locations
                specimen_location, _ = SpecimenLocation.objects.get_or_create(name=row['Specimen_location'])

                specimen = Specimen()
                specimen.specimen_location = specimen_location

                if row['Latitude'] and row['Longitude']:
                    lat = float(row['Latitude'].replace(',','.'))
                    lon = float(row['Longitude'].replace(',','.'))
                    specimen.coords = Point(lon, lat)

                specimen.comment = row['Comment']

                if row['Depth']:
                    if '-' in row['Depth']: # It's a range
                        min, max = row['Depth'].split('-')
                    else:  # Single value
                        min = max = row['Depth']

                specimen.depth = (float(min.replace(',','.')), float(max.replace(',','.')))

                specimen.identified_by = identificator
                specimen.scientific_name = row['Scientific_name']
                specimen.specimen_id = row['Specimen_id']
                specimen.save()
                self.stdout.write(self.style.SUCCESS('OK'))









