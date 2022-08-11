from django.core.management.base import BaseCommand
from faker import Faker

from clinical.models import ClinicalData
from clinical.tests.utils import Provider, create_data


class Command(BaseCommand):
    """Fake data generator for the (initial ad hoc) clinical data model.

    Usage
    -------
        `python manage.py fake_data -n <num samples>`
    """

    help = "Create fake data for the database using faker."

    def add_arguments(self, parser):
        parser.add_argument(
            "-n",
            "--num_samples",
            type=int,
            required=True,
            help="Number of samples generated to the db",
        )

    def handle(self, *args, **kwargs):
        fake = Faker()
        fake.add_provider(Provider)

        for i in range(kwargs["num_samples"]):
            ClinicalData.objects.create(patient=f"patient{i}", **create_data(fake))
