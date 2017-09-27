from django.core import management

from ._utils import AstaporCommand


class Command(AstaporCommand):
    help = 'Call other commands in sequence to perform the full data import and initial processing.'

    def add_arguments(self, parser):
        parser.add_argument('specimen_csv_file')
        parser.add_argument('taxonomy_csv_file')

    def handle(self, *args, **options):
        self.w('1. Importing specimens')
        management.call_command('import_specimens', '--truncate', '{f}'.format(f=options['specimen_csv_file']))

        self.w('2. Importing taxonomy')
        management.call_command('import_taxonomy', '--truncate', '{f}'.format(f=options['taxonomy_csv_file']))

        self.w('3. Reconcile taxonomy')
        management.call_command('reconcile_taxonomy', '--all')

