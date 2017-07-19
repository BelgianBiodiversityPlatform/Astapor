import re

from django.core.management.base import BaseCommand

from specimens.models import Specimen, Taxon

SPXXX_REGEXP = " sp\d+$"

all_genus = Taxon.genus_objects.all()
all_species = Taxon.species_objects.all()
all_families = Taxon.family_objects.all()


def get_genus_with_name(name_to_match):
    return next((genus for genus in all_genus if genus.name == name_to_match), None)


def get_species_with_name(name_to_match):
    return next((species for species in all_species if species.species_name() == name_to_match), None)


def get_family_with_name(name_to_match):
    return next((family for family in all_families if family.name == name_to_match), None)


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

        total_specimens_count = 0
        matched_specimens_count = 0
        undet_specimens_count = 0

        for specimen in Specimen.objects.all():
            name_to_match = specimen.initial_scientific_name
            initial_sn_length = len(specimen.initial_scientific_name.split())
            name_contains_parentheses = '(' in name_to_match or ')' in name_to_match
            taxon_found = False

            if (not specimen.taxon) or options['reconcile_all']:
                total_specimens_count += 1
                self.stdout.write('Specimen {s} (initial scientific name: {sn})...'.format(s=specimen,
                                                                                           sn=name_to_match),
                                  ending='')

                if name_to_match.lower() == "undet":
                    #  It's normal to not match, we just count it separately for stats
                    undet_specimens_count += 1
                    self.stdout.write(self.style.WARNING('Case 1: INITIAL SCIENTIFIC NAME IS UNDET, SKIPPING'))
                # Best case: exact match on species name
                elif get_species_with_name(name_to_match):
                    taxon_found = True
                    self.stdout.write(self.style.SUCCESS('Case 2: FOUND EXACT SPECIES MATCH ON INITIAL SCIENTIFIC NAME'))
                    specimen.taxon = get_species_with_name(name_to_match)
                elif 'cf ' in name_to_match and get_species_with_name(name_to_match.replace('cf ', '')):
                    taxon_found = True
                    self.stdout.write(self.style.SUCCESS('Case 2b: FOUND EXACT SPECIES MATCH ON INITIAL SCIENTIFIC NAME - cf'))
                    specimen.taxon = get_species_with_name(name_to_match.replace('cf ', ''))
                    specimen.uncertain_identification = True
                elif 'cf. ' in name_to_match and get_species_with_name(name_to_match.replace('cf. ', '')):
                    taxon_found = True
                    self.stdout.write(self.style.SUCCESS('Case 2c: FOUND EXACT SPECIES MATCH ON INITIAL SCIENTIFIC NAME - cf.'))
                    specimen.taxon = get_species_with_name(name_to_match.replace('cf. ', ''))
                    specimen.uncertain_identification = True
                elif name_to_match.endswith('sp') or name_to_match.endswith('sp.'):
                    # No species match, we look for a Genus
                    self.stdout.write("Case 3: Dropping 'sp'/'sp.' and looking for a genus or subgenus...", ending='')
                    if name_to_match.endswith('sp'):
                        name_to_match = name_to_match[:-3]
                    elif name_to_match.endswith('sp.'):
                        name_to_match = name_to_match[:-4]

                    genus_found = get_genus_with_name(name_to_match)
                    if genus_found:
                        taxon_found = True
                        self.stdout.write(self.style.SUCCESS('EXACT MATCH ON GENUS NAME after dropping sp/sp.'))
                        specimen.taxon = genus_found
                    elif name_contains_parentheses:
                        # If we have the form 'Cheiraster (Luidiaster) sp', we can try to match it to the subgenus
                        sg_found = Taxon.objects.get_subgenus_from_parentheses_form(name_to_match)
                        if sg_found:
                            taxon_found = True
                            self.stdout.write(self.style.SUCCESS('EXACT MATCH ON SUBGENUS NAME after dropping sp/sp.'))
                            specimen.taxon = sg_found
                        else:
                            self.stdout.write(self.style.ERROR('NO MATCHING SUBGENUS FOUND'))
                    else:
                        self.stdout.write(self.style.ERROR('NO MATCH FOUND IN CASE 3.'))


                # two words, string ends with " sp" followed by digits
                elif initial_sn_length == 2 and (re.search(SPXXX_REGEXP, name_to_match)):
                    name_to_match = re.sub(SPXXX_REGEXP, '', name_to_match)
                    self.stdout.write("Case 4: 2 words + sp + digits: looking for a '{0}' Genus...".format(name_to_match),
                                      ending='')

                    genus_found = get_genus_with_name(name_to_match)
                    if genus_found:
                        taxon_found = True
                        self.stdout.write(self.style.SUCCESS('EXACT MATCH ON GENUS NAME after dropping spXXX'))
                        specimen.taxon = genus_found
                    else:
                        self.stdout.write(self.style.ERROR('NO MATCHING GENUS FOUND'))

                elif initial_sn_length == 1:
                    self.stdout.write("Case 5: Initial scientific name is only one word ({0})...".format(name_to_match),
                                      ending='')

                    # Maybe it's a genus?
                    genus_found = get_genus_with_name(name_to_match)
                    family_found = get_family_with_name(name_to_match)

                    if genus_found:
                        taxon_found = True
                        self.stdout.write(self.style.SUCCESS('EXACT MATCH ON GENUS NAME'))
                        specimen.taxon = genus_found
                    elif family_found:
                        taxon_found = True
                        self.stdout.write(self.style.SUCCESS('EXACT MATCH ON FAMILY NAME'))
                        specimen.taxon = family_found
                    else:
                        self.stdout.write(self.style.ERROR('NO MATCHING GENUS/FAMILY FOUND'))

                else:
                    self.stdout.write(self.style.ERROR('Not matching any case...'))

                if taxon_found:
                    matched_specimens_count += 1
                    specimen.save()

        self.stdout.write("End: matched {cm}/{ct} taxon ({pc} percent).".format(cm=matched_specimens_count,
                                                                                ct=total_specimens_count,
                                                                                pc=str(float(matched_specimens_count)/total_specimens_count*100)))
        self.stdout.write("(counting undets: matched {cm}/{ct} taxon ({pc} percent)).".format(cm=matched_specimens_count + undet_specimens_count,
                                                                                ct=total_specimens_count,
                                                                                pc=str(float(matched_specimens_count + undet_specimens_count) / total_specimens_count * 100)))




