import csv
import gzip
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import structlog

from coding_systems.base.import_data_utils import CodingSystemImporter
from coding_systems.ctv3.models import (
    RawConcept,
    RawConceptHierarchy,
    RawConceptTermMapping,
    RawTerm,
    TPPConcept,
    TPPRelationship,
)

logger = structlog.get_logger()


def import_data(
    release_dir,
    release_name,
    valid_from,
    import_ref=None,
):
    release_dir = Path(release_dir)
    with CodingSystemImporter(
        "ctv3", release_name, valid_from, import_ref
    ) as database_alias:
        import_raw_ctv3(release_dir, database_alias)
        import_tpp_ctv3_data(release_dir, database_alias)


def import_raw_ctv3(release_dir, database_alias):
    release_zipfile = release_dir / "nhs_readctv3_25.0.0_20180401000001.zip"
    with TemporaryDirectory() as tempdir:
        release_zip = ZipFile(release_zipfile)
        logger.info("Extracting", release_zip=release_zip.filename)
        release_zip.extractall(path=tempdir)
        temp_path = Path(tempdir)

        def load_records(filename):
            with open(temp_path / "V3" / filename) as infile:
                yield from csv.reader(infile, delimiter="|", quoting=csv.QUOTE_NONE)

        logger.info("Loading raw CTV3 concepts", filename=release_zipfile)
        RawConcept.objects.using(database_alias).bulk_create(
            RawConcept(
                read_code=r[0],
                status=r[1],
                unknown_field_2=r[2],
                another_concept_id=r[3],
            )
            for r in load_records("Concept.v3")
        )

        RawConceptHierarchy.objects.using(database_alias).bulk_create(
            RawConceptHierarchy(child_id=r[0], parent_id=r[1], list_order=r[2])
            for r in load_records("V3hier.v3")
        )

        RawTerm.objects.using(database_alias).bulk_create(
            RawTerm(term_id=r[0], status=r[1], name_1=r[2], name_2=r[3], name_3=r[4])
            for r in load_records("Terms.v3")
        )

        RawConceptTermMapping.objects.using(database_alias).bulk_create(
            RawConceptTermMapping(concept_id=r[0], term_id=r[1], term_type=r[2])
            for r in load_records("Descrip.v3")
        )


def import_tpp_ctv3_data(release_dir, database_alias):
    def load_records(filename_part):
        filepath = release_dir / f"{filename_part}.csv.gz"
        with gzip.open(filepath, "rt") as infile:
            logger.info("Loading TPP CTV3 data}", file=filepath)
            yield from csv.DictReader(infile)

    assert not TPPRelationship.objects.using(database_alias).exists()
    assert not TPPConcept.objects.using(database_alias).exists()

    TPPConcept.objects.using(database_alias).bulk_create(
        TPPConcept(read_code=r["CTV3Code"], description=r["Description"])
        for r in load_records("ctv3_dictionary")
    )
    TPPRelationship.objects.using(database_alias).bulk_create(
        TPPRelationship(
            ancestor_id=r["ParentCTV3Code"],
            descendant_id=r["ChildCTV3Code"],
            distance=r["ChildToParentDistance"],
        )
        for r in load_records("ctv3_hierarchy")
    )
