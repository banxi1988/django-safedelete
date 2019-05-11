from django.db import models

from safedelete.tests.asserts import assert_soft_delete
from ..config import DELETED_VISIBLE_BY_FIELD
from ..managers import SafeDeleteManager
from ..models import SafeDeleteModel


class PkVisibleManager(SafeDeleteManager):
    _safedelete_visibility = DELETED_VISIBLE_BY_FIELD


class PkVisibleModel(SafeDeleteModel):

    objects = PkVisibleManager()

    name = models.CharField(
        max_length=100
    )


class NameVisibleManager(SafeDeleteManager):
    _safedelete_visibility = DELETED_VISIBLE_BY_FIELD
    _safedelete_visibility_field = 'name'


class NameVisibleField(SafeDeleteModel):
    name = models.CharField(max_length=200, unique=True)

    objects = NameVisibleManager()

    def __str__(self):
        return self.name

import pytest
pytestmark = pytest.mark.django_db

@pytest.fixture()
def instance():
    return PkVisibleModel.objects.create(
        name='instance'
    )

@pytest.fixture()
def namevisiblefield():
    return (
        NameVisibleField.objects.create(name='NVF 1'),
        NameVisibleField.objects.create(name='NVF 2'),
        NameVisibleField.objects.create(name='NVF 3'),
    )


def test_visible_by_pk(instance):
    """Test whether the soft deleted model can be found by filtering on pk."""
    assert_soft_delete(instance, save=False)
    assert PkVisibleModel.objects.filter( pk=instance.pk ).count() == 1
    # Raises PkVisibleModel.DoesNotExist if it isn't found
    PkVisibleModel.objects.get( pk=instance.pk )

def test_invisible_by_name(instance):
    """Test whether the soft deleted model cannot be found by filtering on name."""
    assert_soft_delete(instance, save=False)
    assert PkVisibleModel.objects.filter( name=instance.name ).count() == 0
    pytest.raises(
        PkVisibleModel.DoesNotExist,
        PkVisibleModel.objects.get,
        name=instance.name
    )

def test_access_by_passed_visible_field(namevisiblefield):
    """ Test wether the namefield model can be found by filtering on name. """
    name = namevisiblefield[0].name
    namevisiblefield[0].delete()
    pytest.raises(
        NameVisibleField.DoesNotExist,
        NameVisibleField.objects.get,
        pk=namevisiblefield[0].id
    )
    assert (namevisiblefield[0] == NameVisibleField.objects.get(name=name))
    cat = NameVisibleField.objects.filter(name=name)
    assert (len(cat) == 1)
    assert (namevisiblefield[0] == cat[0])
