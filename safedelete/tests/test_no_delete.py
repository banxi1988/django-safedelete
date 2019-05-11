from ..config import NO_DELETE
from ..models import SafeDeleteModel


class NoDeleteModel(SafeDeleteModel):
    _safedelete_policy = NO_DELETE


import pytest
pytestmark = pytest.mark.django_db

@pytest.fixture()
def instance():
    return NoDeleteModel.objects.create( )

def test_no_delete(instance):
    """Test whether the model's delete is ignored.

    Normally when deleting a model, it can no longer be refreshed from
    the database and will raise a DoesNotExist exception.
    """
    instance.delete()
    instance.refresh_from_db()
    assert instance.deleted is None

def test_no_delete_manager(instance):
    """Test whether models with NO_DELETE are impossible to delete via the manager."""
    NoDeleteModel.objects.all().delete()
    instance.refresh_from_db()
    assert instance.deleted is None
