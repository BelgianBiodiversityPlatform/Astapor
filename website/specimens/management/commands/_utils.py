from django.core.management.base import BaseCommand, CommandError


def validate_number_cols(row, expected_cols_count):
    """Raise CommandError if validation fails."""
    num_cols = len(row)
    if num_cols != expected_cols_count:
        raise CommandError("The source file has {actual_count} columns ({expected_count} expected)".format(
            actual_count=num_cols, expected_count=expected_cols_count))

class AstaporCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(AstaporCommand, self).__init__(*args, **kwargs)

        self.w = self.stdout.write  # Alias to save keystrokes :)