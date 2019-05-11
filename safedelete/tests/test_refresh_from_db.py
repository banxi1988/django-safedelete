from ..config import DELETED_VISIBLE_BY_FIELD
from ..managers import SafeDeleteManager
from ..models import SafeDeleteMixin


class FieldManager(SafeDeleteManager):
    _safedelete_visibility = DELETED_VISIBLE_BY_FIELD


class RefreshModel(SafeDeleteMixin):
    objects = FieldManager()


import pytest
pytestmark = pytest.mark.django_db

@pytest.fixture()
def instance():
    return RefreshModel.objects.create()


def test_visible_by_field(instance):
    """Refresh should work with DELETED_VISIBLE_BY_FIELD."""
    instance.refresh_from_db()

    instance.delete()
    instance.refresh_from_db()
