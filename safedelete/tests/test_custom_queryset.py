from django.db import models

from ..managers import SafeDeleteManager, SafeDeleteQueryset
from ..models import SafeDeleteModel


import pytest
pytestmark = pytest.mark.django_db

class CustomQuerySet(SafeDeleteQueryset):

  def green(self):
    return self.filter(
      color='green'
    )


class CustomManager(SafeDeleteManager):
  _queryset_class = CustomQuerySet

  def green(self):
    """Implemented here so ``green`` available as manager's method
    """
    return self.get_queryset().green()


choices = (
  ('red', "Red"),
  ('green', "Green"),
)


class CustomQuerySetModel(SafeDeleteModel):
  color = models.CharField(
    max_length=5,
    choices=choices
  )

  objects = CustomManager()

  # other manager to test custom QS using ``SafeDeleteManager.__init__``
  other_objects = SafeDeleteManager(CustomQuerySet)

def test_custom_queryset_original_behavior():
  """Test whether creating a custom queryset works as intended."""
  CustomQuerySetModel.objects.create(
    color=choices[0][0]
  )
  CustomQuerySetModel.objects.create(
    color=choices[1][0]
  )

  assert CustomQuerySetModel.objects.count() == 2
  assert CustomQuerySetModel.objects.green().count() == 1

def test_custom_queryset_custom_method():
  """Test custom filters for deleted objects"""
  instance = _create_green_instance()
  instance.delete()

  deleted_only = CustomQuerySetModel.objects.deleted_only()

  # ensure deleted instances available
  assert deleted_only.count() == 1

  # and they can be custom filtered
  assert deleted_only.green().count() == 1

def test_custom_queryset_without_manager():
  """Test whether custom queryset may be used without custom manager
  """
  instance = _create_green_instance()
  instance.delete()

  # note that ``other_objects`` manager used
  deleted_only = CustomQuerySetModel.other_objects.deleted_only()

  # ensure deleted instances available
  assert  deleted_only.count() == 1

  # and they can be custom filtered
  assert  deleted_only.green().count() == 1

def _create_green_instance():
  """Shortcut for creating instance with ``color == green``
  """
  return CustomQuerySetModel.objects.create(color=choices[1][0])
