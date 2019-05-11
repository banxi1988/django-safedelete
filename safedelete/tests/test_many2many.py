from django.db import models

from ..config import DELETED_VISIBLE
from ..models import SafeDeleteModel


class ManyToManyChild(models.Model):
    pass


class ManyToManyParent(SafeDeleteModel):
    children = models.ManyToManyField(
        ManyToManyChild,
        blank=True,
        related_name='parents'
    )


import pytest
pytestmark = pytest.mark.django_db


def test_many_to_many():
    """Test whether related queries still works."""
    parent1 = ManyToManyParent.objects.create()
    parent2 = ManyToManyParent.objects.create()
    child = ManyToManyChild.objects.create()

    parent1.children.add(child)
    parent2.children.add(child)

    # The child should still have both parents
    assert child.parents.all().count() == 2

    # Soft deleting one parent, should "hide" it from the related field
    parent1.delete()
    assert child.parents.all().count() == 1
    # But explicitly saying you want to "show" them, shouldn't hide them
    assert child.parents.all(force_visibility=DELETED_VISIBLE).count() == 2
