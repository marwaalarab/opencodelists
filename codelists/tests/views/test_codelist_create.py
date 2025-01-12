from opencodelists.tests.assertions import assert_difference, assert_no_difference

from ..helpers import csv_builder
from .assertions import (
    assert_get_unauthenticated,
    assert_get_unauthorised,
    assert_post_unauthenticated,
    assert_post_unauthorised,
)
from .helpers import force_login


def test_get_unauthenticated(client, organisation):
    assert_get_unauthenticated(client, organisation.get_codelist_create_url())


def test_post_unauthenticated(client, organisation):
    assert_post_unauthenticated(client, organisation.get_codelist_create_url())


def test_get_unauthorised(client, organisation):
    assert_get_unauthorised(client, organisation.get_codelist_create_url())


def test_post_unauthorised(client, organisation):
    assert_post_unauthorised(client, organisation.get_codelist_create_url())


def test_get_unauthorised_for_user(client, user):
    assert_get_unauthorised(client, user.get_codelist_create_url())


def test_post_unauthorised_for_user(client, user):
    assert_post_unauthorised(client, user.get_codelist_create_url())


def test_get_for_organisation(client, organisation):
    force_login(organisation, client)
    response = client.get(organisation.get_codelist_create_url())
    assert response.status_code == 200


def test_get_for_user(client, user):
    force_login(user, client)
    response = client.get(user.get_codelist_create_url())
    assert response.status_code == 200


def test_post_success(client, organisation, user):
    force_login(organisation, client)

    csv_data = "code,description\n1067731000000107,Injury whilst swimming (disorder)"
    data = {
        "name": "Test Codelist",
        "coding_system_id": "snomedct",
        "coding_system_database_alias": "snomedct_test_20200101",
        "description": "This is a test",
        "methodology": "This is how we did it",
        "csv_data": csv_builder(csv_data),
        "reference-TOTAL_FORMS": "1",
        "reference-INITIAL_FORMS": "0",
        "reference-MIN_NUM_FORMS": "0",
        "reference-MAX_NUM_FORMS": "1000",
        "reference-0-text": "foo",
        "reference-0-url": "http://example.com",
        "signoff-TOTAL_FORMS": "1",
        "signoff-INITIAL_FORMS": "0",
        "signoff-MIN_NUM_FORMS": "0",
        "signoff-MAX_NUM_FORMS": "1000",
        "signoff-0-user": user.username,
        "signoff-0-date": "2020-01-23",
    }

    with assert_difference(organisation.codelists.count, expected_difference=1):
        response = client.post(organisation.get_codelist_create_url(), data=data)

    assert response.status_code == 302
    assert response.url == f"/codelist/{organisation.slug}/test-codelist/"

    codelist = organisation.codelists.last()
    assert codelist.name == "Test Codelist"

    # we should have one reference to example.com
    assert codelist.references.count() == 1
    ref = codelist.references.first()
    assert ref.url == "http://example.com"

    # we should have one signoff
    assert codelist.signoffs.count() == 1
    signoff = codelist.signoffs.first()
    assert signoff.user == user


def test_post_invalid(client, organisation):
    force_login(organisation, client)

    csv_data = "code,description\n1067731000000107,Injury whilst swimming (disorder)"

    # missing signoff-0-user
    data = {
        "name": "Test Codelist",
        "coding_system_id": "snomedct",
        "description": "This is a test",
        "methodology": "This is how we did it",
        "csv_data": csv_builder(csv_data),
        "reference-TOTAL_FORMS": "1",
        "reference-INITIAL_FORMS": "0",
        "reference-MIN_NUM_FORMS": "0",
        "reference-MAX_NUM_FORMS": "1000",
        "reference-0-text": "foo",
        "reference-0-url": "http://example.com",
        "signoff-TOTAL_FORMS": "1",
        "signoff-INITIAL_FORMS": "0",
        "signoff-MIN_NUM_FORMS": "0",
        "signoff-MAX_NUM_FORMS": "1000",
        "signoff-0-date": "2020-01-23",
    }

    with assert_no_difference(organisation.codelists.count):
        response = client.post(organisation.get_codelist_create_url(), data=data)

    # we're returning an HTML response when there are errors so check we don't
    # receive a redirect code
    assert response.status_code == 200

    # confirm we have errors from the signoff formset
    assert response.context_data["signoff_formset"].errors


def test_post_with_duplicate_name(client, organisation):
    force_login(organisation, client)

    csv_data = "code,description\n1067731000000107,Injury whilst swimming (disorder)"
    data = {
        "name": "Old-style Codelist",  # This name is already taken
        "coding_system_id": "snomedct",
        "description": "This is a test",
        "methodology": "This is how we did it",
        "csv_data": csv_builder(csv_data),
        "reference-TOTAL_FORMS": "0",
        "reference-INITIAL_FORMS": "0",
        "reference-MIN_NUM_FORMS": "0",
        "reference-MAX_NUM_FORMS": "1000",
        "signoff-TOTAL_FORMS": "0",
        "signoff-INITIAL_FORMS": "0",
        "signoff-MIN_NUM_FORMS": "0",
        "signoff-MAX_NUM_FORMS": "1000",
    }

    with assert_no_difference(organisation.codelists.count):
        response = client.post(organisation.get_codelist_create_url(), data=data)

    # we're returning an HTML response when there are errors so check we don't
    # receive a redirect code
    assert response.status_code == 200

    # confirm we have errors from the codelist form
    assert response.context_data["codelist_form"].errors == {
        "__all__": ["There is already a codelist called Old-style Codelist"]
    }
