from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .. import actions
from .decorators import load_version, require_permission


@require_POST
@login_required
@load_version
@require_permission
def version_create(request, version):
    coding_system_database_alias = request.POST["coding_system_database_alias"]
    draft = actions.export_to_builder(
        version=version,
        author=request.user,
        coding_system_database_alias=coding_system_database_alias,
    )
    return redirect(draft.get_builder_draft_url())
