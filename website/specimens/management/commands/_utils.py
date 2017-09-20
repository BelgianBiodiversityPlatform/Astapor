from django.core.management.base import BaseCommand


class AstaporCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(AstaporCommand, self).__init__(*args, **kwargs)

        self.w = self.stdout.write  # Alias to save keystrokes :)