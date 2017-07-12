from django.test import TestCase

from django.core.exceptions import ValidationError

from .models import Specimen, Person, SpecimenLocation, Expedition, Station



class SpecimenTestCase(TestCase):
    def setUp(self):
        self.camille = Person.objects.create(first_name="Camille", last_name="Moreau")
        self.ulb = SpecimenLocation.objects.create(name="ULB")
        self.cambio_expedition = Expedition.objects.create(name="ANT XXVII/3 (CAMBIO)")
        self.ps77_station = Station.objects.create(name="PS77/239-3", expedition=self.cambio_expedition)

        self.specimen1 = Specimen.objects.create(specimen_id=1,
                                initial_scientific_name="Acodontaster capitatus",
                                identified_by=self.camille,
                                specimen_location=self.ulb,
                                station=self.ps77_station,
                                vial="100")

        self.specimen2 = Specimen.objects.create(specimen_id=2,
                                                 initial_scientific_name="Acodontaster capitatus",
                                                 identified_by=self.camille,
                                                 specimen_location=self.ulb,
                                                 station=self.ps77_station,
                                                 vial="101")

        self.specimen3 = Specimen.objects.create(specimen_id=3,
                                                 initial_scientific_name="Acodontaster capitatus",
                                                 identified_by=self.camille,
                                                 specimen_location=self.ulb,
                                                 station=self.ps77_station,
                                                 vial="")


    def test_unique_vial_per_expedition(self):
        # Ensure the 'unique vial per expedition rule is respected'
        with self.settings(DISABLE_VIAL_UNIQUENESS_VALIDATION=False):
            # a) same expedition, same station: reject
            with self.assertRaisesMessage(ValidationError, "Vial should be unique for a given expedition"):
                Specimen.objects.create(specimen_id=4,
                                        initial_scientific_name="Acodontaster capitatus",
                                        identified_by=self.camille,
                                        specimen_location=self.ulb,
                                        station=self.ps77_station,
                                        vial="100")


            # b) same expedition, different station: reject
            with self.assertRaisesMessage(ValidationError, "Vial should be unique for a given expedition"):
                Specimen.objects.create(specimen_id=5,
                                        initial_scientific_name="Acodontaster capitatus",
                                        identified_by=self.camille,
                                        specimen_location=self.ulb,
                                        station=Station.objects.create(name="another_station",
                                                                       expedition=self.cambio_expedition),
                                        vial="100")

            # Also reject when editing an existing
            with self.assertRaisesMessage(ValidationError, "Vial should be unique for a given expedition"):
                self.specimen2.vial = "100"
                self.specimen2.save()

            # But allow "duplicate blanks"
            try:
                Specimen.objects.create(specimen_id=6,
                                        initial_scientific_name="Acodontaster capitatus",
                                        identified_by=self.camille,
                                        specimen_location=self.ulb,
                                        station=self.ps77_station,
                                        vial="")
            except ValidationError:
                self.fail("Raised ValidationError unexpectedly!")

    def test_disabled_unique_vial_per_expedition(self):
        # Ensure the 'unique vial per expedition can be disabled in settings'
        with self.settings(DISABLE_VIAL_UNIQUENESS_VALIDATION=True):
            # without the settings, this case would throw an exeption
            try:
                Specimen.objects.create(specimen_id=4,
                                        initial_scientific_name="Acodontaster capitatus",
                                        identified_by=self.camille,
                                        specimen_location=self.ulb,
                                        station=self.ps77_station,
                                        vial="100")
            except ValidationError:
                self.fail("Raised ValidationError while Vial uniqueness is disabled in settings")
