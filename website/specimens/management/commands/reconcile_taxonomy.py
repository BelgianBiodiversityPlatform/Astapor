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
        all_genus = Taxon.genus_objects.all()

        total_specimens_count = 0
        matched_specimens_count = 0

        for specimen in Specimen.objects.all():
            name_to_match = specimen.initial_scientific_name
            taxon_found = False

            if (not specimen.taxon) or options['reconcile_all']:
                total_specimens_count += 1
                self.stdout.write('Specimen {s} (initial scientific name: {sn})...'.format(s=specimen,
                                                                                           sn=name_to_match),
                                  ending='')

                # Best case: exact match on species name
                species_found = next((species for species in all_species if species.species_name() == name_to_match), None)
                if species_found:
                    taxon_found = True
                    self.stdout.write(self.style.SUCCESS('EXACT SPECIES MATCH ON SCIENTIFIC NAME'))
                    specimen.taxon = species_found
                elif name_to_match.endswith('sp'):
                    # No species match, we look for a Genus
                    self.stdout.write("Dropping 'sp' and looking for a genus...", ending='')
                    name_to_match = name_to_match[:-3]

                    genus_found = next((genus for genus in all_genus if genus.name == name_to_match), None)
                    if genus_found:
                        taxon_found = True
                        self.stdout.write(self.style.SUCCESS('EXACT SPECIES MATCH ON GENUS NAME'))
                        specimen.taxon = genus_found

                if taxon_found:
                    matched_specimens_count += 1
                    specimen.save()
                else:
                    self.stdout.write(self.style.ERROR('No matching taxon found'))

        self.stdout.write("End: matched {cm}/{ct} taxon ({pc} percent).".format(cm=matched_specimens_count,
                                                                                ct=total_specimens_count,
                                                                                pc=str(float(matched_specimens_count)/total_specimens_count*100)))




