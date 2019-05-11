from django.db import models

from safedelete.tests.asserts import assert_soft_delete
from ..models import SafeDeleteModel

class InvisibleModel(SafeDeleteModel):
    # SafeDeleteModel subclasses automatically have their visibility set to invisible.

    name = models.CharField(
        max_length=100
    )

import pytest
pytestmark = pytest.mark.django_db

@pytest.fixture()
def instance():
    return InvisibleModel.objects.create(
        name='instance'
    )


def test_visible_by_pk(instance):
    obj = instance
    assert_soft_delete(obj, save=False)
    assert InvisibleModel.objects.filter( pk=obj.pk ).count() == 0
    pytest.raises( InvisibleModel.DoesNotExist, InvisibleModel.objects.get, pk=obj.pk )

def test_invisible_by_name(instance):
    """Test whether the soft deleted model cannot be found by filtering on name."""
    obj = instance
    assert_soft_delete(obj, save=False)
    assert InvisibleModel.objects.filter(
            name=obj.name
        ).count() == 0
    pytest.raises(
        InvisibleModel.DoesNotExist,
        InvisibleModel.objects.get,
        name=obj.name
    )
