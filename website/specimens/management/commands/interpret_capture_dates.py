import datetime
import calendar

from django.core.management.base import CommandError

from specimens.models import Specimen
from ._utils import AstaporCommand

def last_day_of_month(month, year):
    return calendar.monthrange(year, month)[1]


class IncomprehensibleDateException(Exception):
    pass


class Command(AstaporCommand):
    help = 'Try (best effort) to interpret the initial date/year of specimens and set capture_date_start and ' \
           'capture_date_end field'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            dest='set_all',
            default=False,
            help='Also overwrite capture_date_start and capture_date_end if already set',
        )

    def extract_date(self, d):
        """ Returns y, m, d (ints). d is None if we only know the month"""

        if d.count('-') == 2:
            self.w("Date assumed to be in (D)D-(M)M-YY format...")
            d, m, y = d.split("-")
            return int("20{y}".format(y=y)), int(m), int(d)
        elif d.count('-') == 1:
            y, m = d.split("-")
            self.w("Date assumed to be in YYYY-MM format...")
            return int(y), int(m), None

        else:
            raise IncomprehensibleDateException()

    def handle(self, *args, **options):
        self.w('Interpret and set specimen capture dates...')

        if options['set_all']:
            self.w("--all: we will also treat Specimens that already have capture_date_start and "
                              "capture_date_end fields set.")

        i = 0
        solved_cases = 0

        for specimen in Specimen.objects.all():
            if options['set_all'] or (not specimen.capture_date_start and not specimen.capture_date_end):
                i = i + 1
                self.w('Specimen w/ ID={s} (initial year: {year} - initial date: {d})...'.format(s=specimen.specimen_id,
                                                                                                 year=specimen.initial_capture_year,
                                                                                                 d=specimen.initial_capture_date))

                solved = False
                # no date, no year
                if not specimen.initial_capture_year and not specimen.initial_capture_date:
                    self.w(self.style.SUCCESS("No initial data, skipping."))
                    solved = True
                # no date but year
                elif specimen.initial_capture_year and not specimen.initial_capture_date:
                    specimen.capture_date_start = datetime.date(int(specimen.initial_capture_year), 1, 1)
                    specimen.capture_date_end = datetime.date(int(specimen.initial_capture_year), 12, 31)
                    self.w(self.style.SUCCESS("We only have a year..."))
                    solved = True
                # 'date' filled, but not 'year'
                elif not specimen.initial_capture_year and specimen.initial_capture_date:
                    y, m, d = self.extract_date(specimen.initial_capture_date)
                    if d:  # we got a specific date
                        specimen.capture_date_start = datetime.date(y, m, d)
                        specimen.capture_date_end = datetime.date(y, m, d)
                    else:  # we only got a month
                        specimen.capture_date_start = datetime.date(y, m, 1)
                        specimen.capture_date_end = datetime.date(y, m, last_day_of_month(m, y))
                    solved = True
                # both are filled!
                else:
                    # consistency check
                    y, m, d = self.extract_date(specimen.initial_capture_date)

                    if y != int(specimen.initial_capture_year):
                        raise CommandError("Inconsistency detected between year and date")
                    else:
                        if d:  # we got a specific date
                            specimen.capture_date_start = datetime.date(y, m, d)
                            specimen.capture_date_end = datetime.date(y, m, d)
                        else:  # we only got a month
                            specimen.capture_date_start = datetime.date(y, m, 1)
                            specimen.capture_date_end = datetime.date(y, m, last_day_of_month(m, y))

                    solved = True

                if solved:
                    solved_cases = solved_cases + 1
                    specimen.save()

                    self.w('Values set: capture_date_start:{start} - capture_date_end:{end}'.format(
                        start=specimen.capture_date_start,
                        end=specimen.capture_date_end))

        self.w("End: solved {solved}/{total} cases ({pc} percent).".format(solved=solved_cases,
                                                                                      total=i,
                                                                                      pc=str(float(solved_cases) / i * 100)))



