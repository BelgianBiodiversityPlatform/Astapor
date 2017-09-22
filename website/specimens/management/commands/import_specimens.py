import csv

from psycopg2.extras import NumericRange

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import CommandError
from django.contrib.gis.geos import Point

from specimens.models import (Person, SpecimenLocation, Specimen, Fixation, Expedition, Station, Bioregion,
                              Gear, UNKNOWN_STATION_NAME)

from ._utils import AstaporCommand

MODELS_TO_TRUNCATE = [Gear, Station, Expedition, Fixation, Person, SpecimenLocation, Specimen]


class Command(AstaporCommand):
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

    def get_or_create_station_gear_and_expedition(self, station_name, expedition_name, coordinates, depth, gear):
        # Returns a Station object, ready to assign to Specimen.station
        """

        :rtype: Station
        """

        if station_name == '':
            station_name = UNKNOWN_STATION_NAME

        g, _ = Gear.objects.get_or_create(name=gear)

        try:  # A station that match the characteristics already exists
            return Station.objects.get(name=station_name,
                                       expedition__name=expedition_name,
                                       coordinates=coordinates,
                                       depth=depth,
                                       gear=g)

        except ObjectDoesNotExist:  # New station, let's create it (with expedition if needed):
            expedition, created = Expedition.objects.get_or_create(name=expedition_name)
            if created:
                self.w(self.style.SUCCESS('\n\tCreated new Expedition: {0}'.format(expedition)), ending='')

            possible_duplicate = Station.objects.possible_inconsistent_duplicate(name=station_name,
                                                                                 expedition=expedition,
                                                                                 coordinates=coordinates,
                                                                                 depth=depth,
                                                                                 gear=g)

            station = Station.objects.create(name=station_name,
                                             expedition=expedition,
                                             coordinates=coordinates,
                                             depth=depth,
                                             gear=g)
            self.w(self.style.SUCCESS('\n\tCreated new Station: {0}'.format(station.long_str())), ending="")

            if possible_duplicate:
                self.w(self.style.WARNING('\n\t!! Possible inconsistent duplicate for station:'), ending='')
                self.w(self.style.WARNING('\n\tPrevious entry: {0}'.format(possible_duplicate.long_str())), ending='')
                self.w(self.style.WARNING('\n\tNew entry: {0}'.format(station.long_str())), ending='')

            return station

    @staticmethod
    def raw_lat_lon_to_point(raw_lat, raw_lon):
        # Decimal separator: ','
        # Raise CommandError if inconsistency

        raw_lat = raw_lat.strip()
        raw_lon = raw_lon.strip()

        if raw_lat and raw_lon:
            lat = float(raw_lat.replace(',', '.'))
            lon = float(raw_lon.replace(',', '.'))
            return Point(lon, lat)
        elif raw_lat or raw_lon:
            raise CommandError('Either latitude or longitude is missing!')

    @staticmethod
    def raw_depth_to_numericrange(raw_depth):
        depth = raw_depth.strip()
        if depth:
            if '-' in depth:  # It's a range
                d_min, d_max = depth.split('-')
            else:  # Single value
                d_min = d_max = depth

            return NumericRange(float(d_min.replace(',', '.')), float(d_max.replace(',', '.')), bounds='[]')

    def handle(self, *args, **options):
        self.w('Importing data from file...')
        with open(options['csv_file']) as csv_file:
            if options['truncate']:
                for model in MODELS_TO_TRUNCATE:
                    self.w('Truncate model {name}...'.format(name=model.__name__), ending='')
                    model.objects.all().delete()
                    self.w(self.style.SUCCESS('Done.'))

            for i, row in enumerate(csv.DictReader(csv_file, delimiter=',')):
                specimen = Specimen()
                specimen.specimen_id = row['Specimen_id'].strip()

                self.w('Processing row #{i} with ID {id}'.format(i=i, id=specimen.specimen_id), ending='')

                point = self.raw_lat_lon_to_point(row['Latitude'], row['Longitude'])

                # TODO: add gear when found
                specimen.station = self.get_or_create_station_gear_and_expedition(row['Station'].strip(),
                                                                             row['Expedition'].strip(),
                                                                             coordinates = point,
                                                                             depth=self.raw_depth_to_numericrange(row['Depth']),
                                                                             gear='')

                # Identifiers
                identified_by = row['Identified_by'].strip()
                id_first_name, id_last_name = identified_by.split()
                identifier, created = Person.objects.get_or_create(first_name=id_first_name, last_name=id_last_name)
                if created:
                    self.w(self.style.SUCCESS('\n\tCreated new Person: {0}'.format(identifier)), ending='')

                specimen.identified_by = identifier

                # Specimen locations
                specimen_location, created = SpecimenLocation.objects.get_or_create(name=row['Specimen_location'])
                if created:
                    self.w(self.style.SUCCESS('\n\tCreated new Specimen Location: {0}'.format(specimen_location)), ending='')

                specimen.specimen_location = specimen_location

                # Fixation
                fixation = row['Fixation'].strip()
                if fixation:
                    specimen.fixation, created = Fixation.objects.get_or_create(name=fixation)
                    if created:
                        self.w(
                            self.style.SUCCESS('\n\tCreated new Fixation: {0}'.format(specimen.fixation)), ending='')

                bioregion = row['Region'].strip()
                if bioregion:
                    specimen.bioregion, created = Bioregion.objects.get_or_create(name=bioregion)
                    if created:
                        self.w(
                            self.style.SUCCESS('\n\tCreated new Bioregion: {0}'.format(specimen.bioregion)), ending='')

                specimen.vial = row['Vial Size'].strip()
                specimen.mnhn_number = row['Numero_mnhn'].strip()
                specimen.mna_code = row['MNA_code'].strip()
                specimen.bold_process_id = row['BOLD Process ID'].strip()
                specimen.bold_sample_id = row['BOLD Sample ID'].strip()
                specimen.bold_bin = row['BOLD BIN'].strip()
                specimen.sequence_name = row['Sequence_name'].strip()

                # Load raw/messy/imprecise dates:
                specimen.initial_capture_year = row['Year'].strip()
                specimen.initial_capture_date = row['Date'].strip()

                specimen.initial_scientific_name = row['Scientific_name'].strip()

                specimen.comment = row['Comment'].strip()

                specimen.save()
                self.w(self.style.SUCCESS('\n\t => Specimen created.'))
