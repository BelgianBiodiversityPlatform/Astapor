import csv

from psycopg2.extras import NumericRange

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point

from specimens.models import Person, SpecimenLocation, Specimen, Fixation

MODELS_TO_TRUNCATE = [Fixation, Person, SpecimenLocation, Specimen]

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
                for model in MODELS_TO_TRUNCATE:
                    self.stdout.write('Truncate model {name} '.format(name=model.__name__), ending='')
                    model.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS('OK'))

            for i, row in enumerate(csv.DictReader(csv_file, delimiter=',')):
                self.stdout.write('Processing row #{i}...'.format(i=i), ending='')
                specimen = Specimen()

                # Identificators
                identified_by = row['Identified_by'].strip()
                id_first_name, id_last_name = identified_by.split()
                identificator, _ = Person.objects.get_or_create(first_name=id_first_name, last_name=id_last_name)
                specimen.identified_by = identificator

                # Specimen locations
                specimen_location, _ = SpecimenLocation.objects.get_or_create(name=row['Specimen_location'])
                specimen.specimen_location = specimen_location

                # Coordinates
                if row['Latitude'] and row['Longitude']:
                    lat = float(row['Latitude'].replace(',','.'))
                    lon = float(row['Longitude'].replace(',','.'))
                    specimen.coords = Point(lon, lat)

                # Fixation
                fixation = row['Fixation'].strip()
                if fixation:
                    specimen.fixation, _ = Fixation.objects.get_or_create(name=fixation)


                specimen.comment = row['Comment']

                depth = row['Depth'].strip()
                if depth:
                    if '-' in depth: # It's a range
                        d_min, d_max = depth.split('-')
                    else:  # Single value
                        d_min = d_max = depth

                    specimen.depth = NumericRange(float(d_min.replace(',','.')), float(d_max.replace(',','.')), bounds='[]')

                specimen.scientific_name = row['Scientific_name']
                specimen.specimen_id = row['Specimen_id']
                specimen.save()
                self.stdout.write(self.style.SUCCESS('OK'))









