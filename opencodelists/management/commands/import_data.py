import argparse
import glob
import os
import sys
from datetime import datetime
from importlib import import_module

from django.core.management import BaseCommand

from codelists.coding_systems import CODING_SYSTEMS
from coding_systems.versioning.models import CodingSystemRelease


def iter_possible_modules():
    paths = glob.glob("**/import_data.py", recursive=True)

    for path in paths:
        head, _ = os.path.split(path)
        yield head.replace(os.sep, ".")


def valid_from(input_date):
    try:
        return datetime.strptime(input_date, "%Y%m%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date (YYYYMMDD): {input_date}")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dataset")
        parser.add_argument("release_dir")
        parser.add_argument("--release", dest="release_name", help="Release name")
        parser.add_argument(
            "--valid-from",
            type=valid_from,
            help="For coding system imports: date the release is valid from, in YYYYMMDD format",
        )
        parser.add_argument(
            "--import-ref",
            help="For coding system imports: optional reference for this import",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force an overwrite of a coding system release",
        )

    def handle(
        self,
        dataset,
        release_dir,
        release_name,
        valid_from,
        import_ref,
        force,
        **kwargs,
    ):
        try:
            mod = import_module(dataset + ".import_data")
        except ModuleNotFoundError:
            self.stdout.write(
                f"Could not find an 'import_data.py' module at path '{dataset}'"
            )
            self.stdout.write("Maybe you meant one of these module paths?")

            possibilities = list(iter_possible_modules())
            for possibility in possibilities:
                self.stdout.write(possibility)

            sys.exit(1)

        module_name = dataset.rsplit(".", 1)[-1]
        if module_name in CODING_SYSTEMS:
            import_data_kwargs = self.get_coding_system_kwargs(
                module_name, release_name, valid_from, import_ref, force
            )
        else:
            import_data_kwargs = {}

        fn = getattr(mod, "import_data")
        fn(release_dir, **import_data_kwargs)

    def get_coding_system_kwargs(
        self, coding_system, release_name, valid_from, import_ref, force
    ):
        if not all([release_name, valid_from]):
            self.stdout.write(
                f"--release and --valid-from are required when importing {coding_system} data"
            )
            sys.exit(1)
        else:
            if (
                CodingSystemRelease.objects.filter(
                    coding_system=coding_system,
                    release_name=release_name,
                    valid_from=valid_from,
                ).exists()
                and not force
            ):
                self.stdout.write(
                    f"A coding system release already exists for {coding_system} with release '{release_name}' and "
                    f"valid from date {valid_from.strftime('%Y%m%d')}. Use the --force option to overwrite "
                    "an existing release"
                )
                sys.exit(1)

        return {
            "release_name": release_name,
            "valid_from": valid_from,
            "import_ref": import_ref,
        }
