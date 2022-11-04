from abc import ABC

from django.utils.functional import cached_property

from coding_systems.versioning.models import CodingSystemRelease


class BaseCodingSystem(ABC):
    """
    A base class for coding systems.
    A CodingSystem is intended to be the interface to a coding system, and represents
    a single version of a specific coding system.
    No models contained within coding_system apps (including the `versioning` app)
    should be accessed directly.
    """

    id = NotImplemented
    name = NotImplemented
    short_name = NotImplemented
    root = None

    def __init__(self, database_alias):
        self.database_alias = database_alias

    @classmethod
    def most_recent(cls):
        """
        Return a CodingSystem instance for the most recent release.
        """
        most_recent_release = CodingSystemRelease.objects.most_recent(cls.id)
        if most_recent_release is None:
            raise CodingSystemRelease.DoesNotExist(
                f"No coding system data found for {cls.short_name}"
            )
        return cls(database_alias=most_recent_release.database_alias)

    @classmethod
    def get_by_release_or_most_recent(cls, database_alias=None):
        """
        Returns a CodingSystem instance for the requested release, or the most recent one.
        """
        database_alias = cls.validate_db_alias(database_alias)
        return cls(database_alias=database_alias)

    @classmethod
    def validate_db_alias(cls, database_alias):
        """
        Ensure that this database_alias is associated with a valid CodingSystemRelease
        If no database_alias is provided, default to the most recent one.
        """
        if database_alias is None:
            return cls.most_recent().database_alias
        all_slugs = CodingSystemRelease.objects.filter(
            coding_system=cls.id
        ).values_list("database_alias", flat=True)
        assert (
            database_alias in all_slugs
        ), f"{database_alias} is not a valid database alias for a {cls.short_name} release."
        return database_alias

    @cached_property
    def release(self):
        return CodingSystemRelease.objects.get(database_alias=self.database_alias)

    @cached_property
    def release_name(self):
        return self.release.release_name

    def search_by_term(self, term):
        raise NotImplementedError

    def search_by_code(self, code):
        raise NotImplementedError

    def lookup_names(self, codes):
        raise NotImplementedError

    def code_to_term(self, codes):
        raise NotImplementedError

    def codes_by_type(self, codes, hierarchy):
        raise NotImplementedError


class DummyCodingSystem(BaseCodingSystem):
    """
    Represents a CodingSystem that will never have an associated database.
    The database alias is set to an string value for any old codelist versions using
    it, so that the not-null constraint on CodelistVersion.coding_system_version_slug
    isn't violated
    """

    def __init__(self, database_alias):
        super().__init__(database_alias="none")

    @classmethod
    def most_recent(cls):
        return cls(database_alias="none")
