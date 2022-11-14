from datetime import date
from pathlib import Path
from unittest.mock import patch

from codelists.coding_systems import CODING_SYSTEMS
from codelists.hierarchy import Hierarchy
from coding_systems.conftest import mock_migrate_coding_system
from coding_systems.ctv3.import_data import import_data
from coding_systems.ctv3.models import RawConcept, TPPConcept
from coding_systems.versioning.models import CodingSystemRelease

MOCK_CTV3_IMPORT_DATA_PATH = Path(__file__).parents[1] / "fixtures" / "import_resources"


def test_import_data(coding_systems_tmp_path, settings):
    cs_release_count = CodingSystemRelease.objects.count()

    # import mock CTV3 data
    # This consists of a very small subset of the hierarchy for Extrinsic asthma - atopy (& pollen)(XE0ZP)
    # Plus codes for types and root concept

    # ...../Xa001/Xa003 Root Concept/Type
    # Xa00B Clinical findings type
    # XaBVJ Clinical findings
    # X0003  └ Disorders
    # H....     └ Respiratory disorder
    # H33..        └ Asthma
    # X101x           └ Allergic asthma
    # XE0YQ               └ Allergic atopic asthma
    # XE0ZP                   └ Extrinsic asthma - atopy (& pollen)

    # And mock TPP data
    # Consists of the same codes and their hierarchy

    with patch(
        "coding_systems.base.import_data_utils.call_command", mock_migrate_coding_system
    ):
        import_data(
            str(MOCK_CTV3_IMPORT_DATA_PATH),
            release_name="v1",
            valid_from=date(2022, 10, 1),
            import_ref="Ref",
        )
    # A new CodingSystemRelease has been created
    assert CodingSystemRelease.objects.count() == cs_release_count + 1
    cs_release = CodingSystemRelease.objects.latest("id")
    assert cs_release.coding_system == "ctv3"
    assert cs_release.release_name == "v1"
    assert cs_release.valid_from == date(2022, 10, 1)
    assert cs_release.import_ref == "Ref"
    assert cs_release.database_alias in settings.DATABASES

    assert RawConcept.objects.using("ctv3_v1_20221001").count() == 11
    assert TPPConcept.objects.using("ctv3_v1_20221001").count() == 11

    # The coding system can correctly identify codes_by_type from the imported data
    latest_coding_system = CODING_SYSTEMS["ctv3"].get_by_release_or_most_recent()
    hierarchy = Hierarchy.from_codes(latest_coding_system, ["XE0ZP", "Xa00B"])
    # no codes returns empty dict
    assert latest_coding_system.codes_by_type([], hierarchy) == {}
    # codes returned by type
    assert latest_coding_system.codes_by_type(["XE0ZP", "X101x"], hierarchy) == {
        "Clinical findings": ["XE0ZP", "X101x"]
    }
