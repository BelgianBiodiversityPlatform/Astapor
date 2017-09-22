from django.forms import widgets
from django.contrib.gis.geos import Point


class LatLongWidget(widgets.MultiWidget):
    """
    A Widget that splits Point input into latitude/longitude text inputs.
    """
    template_name = 'django/forms/widgets/latlong.html'

    def __init__(self, attrs=None):
        _widgets = (
            widgets.TextInput(attrs=attrs),
            widgets.TextInput(attrs=attrs),
        )

        super(LatLongWidget, self).__init__(_widgets, attrs)

    def get_context(self, name, value, attrs):
        context = super(LatLongWidget, self).get_context(name, value, attrs)
        context['lat_label'] = "Lat:"
        context['long_label'] = "Lon:"
        return context

    def decompress(self, value):
        if value:
            return tuple(value.coordinates)
        return (None, None)

    def value_from_datadict(self, data, files, name):
        mylat = data[name + '_0']
        mylong = data[name + '_1']

        try:
            point = Point(float(mylat), float(mylong))
        except ValueError:
            return ''

        return point
