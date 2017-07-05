import re

from django.core.management.base import BaseCommand

from specimens.models import Specimen, Taxon

SPXXX_REGEXP = " sp\d+$"

all_genus = Taxon.genus_objects.all()


def get_genus_with_name(name_to_match):
    return next((genus for genus in all_genus if genus.name == name_to_match), None)


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
            name_to_match = specimen.initial_scientific_name
            initial_sn_length = len(specimen.initial_scientific_name.split())
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
                elif name_to_match.endswith('sp') or name_to_match.endswith('sp.'):
                    # No species match, we look for a Genus
                    self.stdout.write("Dropping 'sp' and looking for a genus...", ending='')
                    if name_to_match.endswith('sp'):
                        name_to_match = name_to_match[:-3]
                    elif name_to_match.endswith('sp.'):
                        name_to_match = name_to_match[:-4]

                    genus_found = get_genus_with_name(name_to_match)
                    if genus_found:
                        taxon_found = True
                        self.stdout.write(self.style.SUCCESS('EXACT SPECIES MATCH ON GENUS NAME'))
                        specimen.taxon = genus_found

                # two words, string ends with " sp" followed by digits
                elif initial_sn_length == 2 and (re.search(SPXXX_REGEXP, name_to_match)):
                    name_to_match = re.sub(SPXXX_REGEXP, '', name_to_match)
                    self.stdout.write("2 words + sp + digits: looking for a '{0}' Genus...".format(name_to_match),
                                      ending='')

                    genus_found = get_genus_with_name(name_to_match)
                    if genus_found:
                        taxon_found = True
                        self.stdout.write(self.style.SUCCESS('EXACT SPECIES MATCH ON GENUS NAME'))
                        specimen.taxon = genus_found

                elif initial_sn_length == 1:
                    self.stdout.write("Initial scientific name is only one word ({0})...".format(name_to_match),
                                      ending='')

                    # Maybe it's a genus?
                    genus_found = get_genus_with_name(name_to_match)
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




