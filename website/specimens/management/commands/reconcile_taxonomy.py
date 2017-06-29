from django.core.management.base import BaseCommand

from specimens.models import Specimen, Taxon

class Command(BaseCommand):
    help = 'Try (best effort) to attach a Taxon to each Specimen according to the initial_scientific_name'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            dest='reconcile_all',
            default=False,
            help='Also reconcile Specimens that are already linked to a Taxon',
        )

    def handle(self, *args, **options):
        self.stdout.write('Attempting to attach taxa to specimens...')

        if options['reconcile_all']:
            self.stdout.write("--all: we will also reconcile Specimens that are already linked to a Taxon.")

        all_species = Taxon.species_objects.all()

        total_specimens_count = 0
        matched_specimens_count = 0

        for specimen in Specimen.objects.all():
            if (not specimen.taxon) or options['reconcile_all']:
                total_specimens_count += 1
                matched_specimens_count += 1  # We'll decrement later if nothing is found...
                self.stdout.write('Specimen {s} (initial scientific name: {sn})...'.format(s=specimen,
                                                                                           sn=specimen.initial_scientific_name),
                                  ending='')

                # Best case: exact match on species name
                found = next((species for species in all_species if species.species_name() == specimen.initial_scientific_name), None)
                if found:
                    self.stdout.write(self.style.SUCCESS('EXACT SPECIES MATCH ON SCIENTIFIC NAME'))
                    specimen.taxon = found
                else:
                    matched_specimens_count -= 1
                    self.stdout.write(self.style.ERROR('No matching taxon found'))

                specimen.save()

        self.stdout.write("End: matched {cm}/{ct} taxon ({pc} percent).".format(cm=matched_specimens_count,
                                                                                ct=total_specimens_count,
                                                                                pc=str(float(matched_specimens_count)/total_specimens_count*100)))




