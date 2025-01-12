import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from . import views

users_patterns = [
    path("<username>/", views.user, name="user"),
    path(
        "<username>/new-codelist/",
        views.user_create_codelist,
        name="user-create-codelist",
    ),
]

organisations_patterns = [
    # list users for an organisation (admins only)
    path(
        "<organisation_slug>/users",
        views.organisation_members,
        name="organisation_members",
    ),
    path("", views.organisations, name="organisations"),
]

urlpatterns = [
    path("", include("codelists.urls")),
    path("api/v1/", include("codelists.api_urls")),
    path("users/", include(users_patterns)),
    path("superusers/", include("superusers.urls")),
    path("organisations/", include(organisations_patterns)),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", views.register, name="register"),
    path("builder/", include("builder.urls")),
    path("conversions/", include("conversions.urls")),
    path("docs/", include("userdocs.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
    path("robots.txt", RedirectView.as_view(url=settings.STATIC_URL + "robots.txt")),
]
