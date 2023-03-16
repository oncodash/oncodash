from django.core.management.base import BaseCommand

from explainer.models import NetworkSpec
from explainer.api.utils import IndTab2Json, split_samplestr


class Command(BaseCommand):
    """
    Django command to populate an empty database table with nodelink-data
    extracted from a indication table (csv).

    Used from the command line

    Example:
    --------
        `python manage.py populate -p /path/to/indicationtable.csv/`
    """

    help = "Convert an indication table (csv) to nodelink-json and populate db"

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--path",
            type=str,
            required=True,
            help="Path to the indication table (csv)",
        )

    def handle(self, *args, **kwargs) -> None:
        converter = IndTab2Json(
            kwargs["path"],
            group_key="Patient",
            certainty_key="certainty",
            df_transform=split_samplestr,
        )

        self.stdout.write("Writing nodelinkdata to db...")
        for patient, spec in converter.network_spec.items():
            net = NetworkSpec(patient=patient, spec=spec)
            net.save()

        self.stdout.write("Finished.")
