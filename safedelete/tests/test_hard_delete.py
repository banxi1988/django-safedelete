from safedelete.tests.asserts import assert_hard_delete
from ..config import HARD_DELETE
from ..models import SafeDeleteModel


class HardDeleteModel(SafeDeleteModel):
    _safedelete_policy = HARD_DELETE

import pytest
pytestmark = pytest.mark.django_db

@pytest.fixture()
def instance():
    return HardDeleteModel.objects.create()


def test_harddelete(instance):
    """Deleting a model with the soft delete policy should only mask it, not delete it."""
    assert_hard_delete(instance)

def test_update_or_create_no_unique_field(instance):
    HardDeleteModel.objects.update_or_create(id=instance.id)
    obj, created = HardDeleteModel.objects.update_or_create(id=instance.id)
    assert obj.id == instance.id
