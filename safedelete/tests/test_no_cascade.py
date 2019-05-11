from django.db import models
from django.db.models.deletion import ProtectedError

from safedelete.tests.asserts import assert_soft_delete, assert_hard_delete
from ..config import HARD_DELETE_NOCASCADE
from ..models import SafeDeleteModel


class NoCascadeModel(SafeDeleteModel):
    _safedelete_policy = HARD_DELETE_NOCASCADE


class CascadeChild(models.Model):
    parent = models.ForeignKey(
        NoCascadeModel,
        on_delete=models.CASCADE
    )


class ProtectedChild(models.Model):
    parent = models.ForeignKey(
        NoCascadeModel,
        on_delete=models.PROTECT
    )


class NullChild(models.Model):
    parent = models.ForeignKey(
        NoCascadeModel,
        on_delete=models.SET_NULL,
        null=True
    )


class DefaultChild(models.Model):
    parent = models.ForeignKey(
        NoCascadeModel,
        on_delete=models.SET_DEFAULT,
        null=True,
        default=None
    )


def get_default():
    return None


class SetChild(models.Model):
    parent = models.ForeignKey(
        NoCascadeModel,
        on_delete=models.SET(get_default),
        null=True,
        default=None
    )


import pytest
pytestmark = pytest.mark.django_db

@pytest.fixture()
def instance():
    return NoCascadeModel.objects.create( )

def test_cascade(instance):
    cascade_child = CascadeChild.objects.create(
        parent=instance
    )
    assert_soft_delete(instance)
    cascade_child.delete()
    assert_hard_delete(instance)

def test_protected(instance):
    ProtectedChild.objects.create(
        parent=instance
    )
    pytest.raises(
        ProtectedError,
        instance.delete
    )

def test_null(instance):
    NullChild.objects.create(
        parent=instance
    )
    assert_hard_delete(instance)

def test_default(instance):
    DefaultChild.objects.create(
        parent=instance
    )
    assert_hard_delete(instance)

def test_set(instance):
    SetChild.objects.create(
        parent=instance
    )
    assert_hard_delete(instance)