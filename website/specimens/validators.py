import datetime

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.deconstruct import deconstructible


def plausible_specimen_date(value):
    if value > datetime.date.today():
        raise ValidationError(_('Specimen capture dates should be in the past, not the future :)'))


@deconstructible
class StrictlyMinValueValidator(MinValueValidator):
    message = _('Ensure this value is greater than %(limit_value)s (not included).')
    code = 'min_value'

    def compare(self, a, b):
        return a <= b