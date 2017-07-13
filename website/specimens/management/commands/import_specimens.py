import csv

from psycopg2.extras import NumericRange

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point

from specimens.models import Person, SpecimenLocation, Specimen, Fixation, Expedition, Station, UNKNOWN_STATION_NAME

MODELS_TO_TRUNCATE = [Station, Expedition, Fixation, Person, SpecimenLocation, Specimen]

# TODO: document use of this script:
# - Column name is important, not column order
# - Lat/lon use comma as a separator


class Command(BaseCommand):
    help = 'Import specimens from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file')

        parser.add_argument(
            '--truncate',
            action='store_true',
            dest='truncate',
            default=False,
            help='Truncate specimens (and related) tables prior to import',
        )

    def get_or_create_station_and_expedition(self, station_name, expedition_name):
        # Returns a Station object, ready to assign to Specimen.station
        """

        :rtype: Station
        """
        if station_name == '':
            station_name = UNKNOWN_STATION_NAME

        try:  # A station already exists for the correct expedition?
            return Station.objects.get(name=station_name, expedition__name=expedition_name)

        except ObjectDoesNotExist:  # New station, let's create it (with expedition if needed):
            expedition, created = Expedition.objects.get_or_create(name=expedition_name)
            if created:
                self.stdout.write(self.style.SUCCESS('Created new expedition: {0}...'.format(expedition)), ending='')

            station = Station.objects.create(name=station_name, expedition=expedition)
            self.stdout.write(self.style.SUCCESS('Created new station: {0}...'.format(station)), ending='')

            return station

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

                specimen.specimen_id = row['Specimen_id'].strip()

                self.stdout.write('Specimen ID is {id}...'.format(id=specimen.specimen_id), ending='')
                specimen.station = self.get_or_create_station_and_expedition(row['Station'].strip(),
                                                                             row['Expedition'].strip())

                # Identifiers
                identified_by = row['Identified_by'].strip()
                id_first_name, id_last_name = identified_by.split()
                identifier, created = Person.objects.get_or_create(first_name=id_first_name, last_name=id_last_name)
                if created:
                    self.stdout.write(self.style.SUCCESS('Created new person: {0}...'.format(identifier)), ending='')

                specimen.identified_by = identifier

                # Specimen locations
                specimen_location, created = SpecimenLocation.objects.get_or_create(name=row['Specimen_location'])
                if created:
                    self.stdout.write(self.style.SUCCESS('Created new Specimen Location: {0}...'.format(specimen_location)),
                                      ending='')

                specimen.specimen_location = specimen_location

                # Coordinates
                latitude = row['Latitude'].strip()
                longitude = row['Longitude'].strip()
                if latitude and longitude:
                    lat = float(row['Latitude'].replace(',','.'))
                    lon = float(row['Longitude'].replace(',','.'))
                    specimen.coords = Point(lon, lat)
                else:
                    if latitude or longitude:
                        raise CommandError('Either latitude or longitude is missing!')

                # Fixation
                fixation = row['Fixation'].strip()
                if fixation:
                    specimen.fixation, created = Fixation.objects.get_or_create(name=fixation)
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS('Created new Fixation: {0}...'.format(specimen.fixation)),ending='')

                specimen.comment = row['Comment']

                depth = row['Depth'].strip()
                if depth:
                    if '-' in depth: # It's a range
                        d_min, d_max = depth.split('-')
                    else:  # Single value
                        d_min = d_max = depth

                    specimen.depth = NumericRange(float(d_min.replace(',','.')), float(d_max.replace(',','.')), bounds='[]')

                specimen.vial = row['Vial'].strip()
                specimen.mnhn_number = row['Numero_mnhn'].strip()
                specimen.mna_code = row['MNA_code'].strip()
                specimen.bold_process_id = row['BOLD Process ID'].strip()
                specimen.bold_sample_id = row['BOLD Sample ID'].strip()
                specimen.bold_bin = row['BOLD BIN'].strip()
                specimen.sequence_name = row['Sequence_name'].strip()
                
                specimen.initial_scientific_name = row['Scientific_name'].strip()

                specimen.save()
                self.stdout.write(self.style.SUCCESS('OK'))









