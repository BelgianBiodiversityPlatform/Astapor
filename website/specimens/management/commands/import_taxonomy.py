import csv

from django.core.management.base import BaseCommand

from specimens.models import TaxonRank, Taxon, TaxonStatus, SPECIES_RANK_NAME, SUBGENUS_RANK_NAME

MODELS_TO_TRUNCATE = [Taxon, TaxonRank, TaxonStatus]


def create_initial_ranks():
    TaxonRank.objects.bulk_create([
        TaxonRank(name='Kingdom'),
        TaxonRank(name='Phylum'),
        TaxonRank(name='Class'),
        TaxonRank(name='Order'),
        TaxonRank(name='Family'),
        TaxonRank(name='Genus'),
        TaxonRank(name=SUBGENUS_RANK_NAME),
        TaxonRank(name=SPECIES_RANK_NAME)
    ])


class Command(BaseCommand):
    help = 'Import taxonomy from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file')

        parser.add_argument(
            '--truncate',
            action='store_true',
            dest='truncate',
            default=False,
            help='Truncate all tables prior to import',
        )

    def handle(self, *args, **options):
        self.stdout.write('Importing data from file...')

        with open(options['csv_file']) as csv_file:
            if options['truncate']:
                for model in MODELS_TO_TRUNCATE:
                    self.stdout.write('Truncate model {name} ...'.format(name=model.__name__), ending='')
                    model.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS('OK'))

            self.stdout.write('Creating initial ranks...')
            create_initial_ranks()

            for i, row in enumerate(csv.DictReader(csv_file, delimiter=',')):
                self.stdout.write('Processing row #{i}...'.format(i=i), ending='')

                species_status, _ = TaxonStatus.objects.get_or_create(name=row['Status'])

                # Starting from the higher ranks
                kingdom, _ = Taxon.objects.get_or_create(name=row['Kingdom'].strip(),
                                                         rank=TaxonRank.objects.get(name="Kingdom"))
                phylum, _ = Taxon.objects.get_or_create(name=row['Phylum'].strip(),
                                                        rank=TaxonRank.objects.get(name="Phylum"),
                                                        parent=kingdom)
                class_taxon, _ = Taxon.objects.get_or_create(name=row['Class'].strip(),
                                                          rank=TaxonRank.objects.get(name="Class"),
                                                          parent=phylum)
                order_taxon, _ = Taxon.objects.get_or_create(name=row['Order'].strip(),
                                                             rank=TaxonRank.objects.get(name="Order"),
                                                             parent=class_taxon)
                family, _ = Taxon.objects.get_or_create(name=row['Family'].strip(),
                                                        rank=TaxonRank.objects.get(name="Family"),
                                                        parent=order_taxon)
                genus, _ = Taxon.objects.get_or_create(name=row['Genus'].strip(),
                                                        rank=TaxonRank.objects.get(name="Genus"),
                                                        parent=family)
                # Subgenus rank is optional
                subgenus_source = row['Subgenus'].strip()
                if subgenus_source:
                    subgenus, _ = Taxon.objects.get_or_create(name=subgenus_source,
                                                              rank=TaxonRank.objects.get(name=SUBGENUS_RANK_NAME),
                                                              parent=genus)

                species_parent = subgenus if subgenus_source else genus
                species, _ = Taxon.objects.get_or_create(name=row['Species'].strip(),
                                                         rank=TaxonRank.objects.get(name=SPECIES_RANK_NAME),
                                                         parent=species_parent,
                                                         status=species_status,
                                                         aphia_id=row['Aphia_ID'].strip(),
                                                         authority=row['Authority'].strip())


                self.stdout.write(self.style.SUCCESS('OK'))

