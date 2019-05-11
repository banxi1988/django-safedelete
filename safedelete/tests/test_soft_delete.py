from safedelete.tests.asserts import assert_soft_delete

from unittest import mock

from django.core.exceptions import ValidationError
from django.db import models
from django.test import override_settings

from ..models import SafeDeleteMixin
from ..models import SafeDeleteModel
from ..config import SOFT_DELETE_CASCADE


class SoftDeleteModel(SafeDeleteModel):
    # SafeDeleteModel has the soft delete policy by default
    pass


class SoftDeleteRelatedModel(SafeDeleteModel):
    related = models.ForeignKey(SoftDeleteModel, on_delete=models.CASCADE)


class SoftDeleteMixinModel(SafeDeleteMixin):
    # Legacy compatibility with the older SafeDeleteMixin name.
    pass


class UniqueSoftDeleteModel(SafeDeleteModel):

    name = models.CharField(
        max_length=100,
        unique=True
    )

import pytest
pytestmark = pytest.mark.django_db

@pytest.fixture()
def instance():
    return SoftDeleteModel.objects.create( )


def test_softdelete(instance):
    """Deleting a model with the soft delete policy should only mask it, not delete it."""
    assert_soft_delete(instance)


def test_softdelete_mixin():
    """Deprecated: Deleting a SafeDeleteMixin model with the soft delete policy should only mask it, not delete it."""
    assert_soft_delete(SoftDeleteMixinModel.objects.create())


def test_signals(instance):
    """The soft delete and undelete signals should be sent correctly for soft deleted models."""
    with mock.patch('safedelete.models.post_undelete.send') as mock_undelete:
      with mock.patch('safedelete.models.post_softdelete.send') as mock_softdelete:
        with mock.patch('safedelete.models.pre_softdelete.send') as mock_presoftdelete:
          instance.delete()
          # Soft deleting the model should've sent a pre_softdelete and a post_softdelete signals.
          assert  mock_presoftdelete.call_count == 1

          assert  mock_softdelete.call_count == 1

          # Saving makes it undelete the model.
          # Undeleting a model should call the post_undelete signal.
          instance.save()
          assert mock_undelete.call_count == 1


def test_undelete(instance):
    """Undeleting a soft deleted model should uhhh... undelete it?"""
    assert_soft_delete(instance, save=False)
    instance.undelete()
    assert SoftDeleteModel.objects.count() == 1
    assert SoftDeleteModel.all_objects.count() == 1



def test_undelete_queryset(instance):
    assert SoftDeleteModel.objects.count() == 1

    SoftDeleteModel.objects.all().delete()
    assert SoftDeleteModel.objects.count() == 0

    SoftDeleteModel.objects.all().undelete()  # Nonsense
    assert SoftDeleteModel.objects.count() == 0

    SoftDeleteModel.deleted_objects.all().undelete()
    assert SoftDeleteModel.objects.count() == 1


def test_undelete_with_soft_delete_policy_and_forced_soft_delete_cascade_policy(instance):
    assert SoftDeleteModel.objects.count() == 1
    SoftDeleteRelatedModel.objects.create(related=SoftDeleteModel.objects.first())
    assert SoftDeleteRelatedModel.objects.count() == 1

    SoftDeleteModel.objects.all().delete()
    assert SoftDeleteModel.objects.count() == 0

    SoftDeleteRelatedModel.objects.all().delete()
    assert SoftDeleteRelatedModel.objects.count() == 0

    SoftDeleteModel.deleted_objects.all().undelete(force_policy=SOFT_DELETE_CASCADE)
    assert SoftDeleteModel.objects.count() == 1
    assert SoftDeleteRelatedModel.objects.count() == 1


def test_validate_unique(instance):
    """Check that uniqueness is also checked against deleted objects """
    UniqueSoftDeleteModel.objects.create(
        name='test'
    ).delete()
    pytest.raises(
        ValidationError,
        UniqueSoftDeleteModel( name='test' ).validate_unique
    )


def test_check_unique_fields_exists(instance):
    # No unique fields
    assert SoftDeleteModel.has_unique_fields() == False
    assert UniqueSoftDeleteModel.has_unique_fields() == True


def test_update_or_create_no_unique_field(instance):
    SoftDeleteModel.objects.update_or_create(id=1)
    obj, created = SoftDeleteModel.objects.update_or_create(id=1)
    assert obj.id == 1


def test_update_or_create_with_unique_field(instance):
    # Create and soft-delete object
    obj, created = UniqueSoftDeleteModel.objects.update_or_create(name='unique-test')
    obj.delete()
    # Update it and see if it fails
    obj, created = UniqueSoftDeleteModel.objects.update_or_create(name='unique-test')
    assert obj.name == 'unique-test'
    assert created == False


@override_settings(SAFE_DELETE_INTERPRET_UNDELETED_OBJECTS_AS_CREATED=True)
def test_update_or_create_flag_with_settings_flag_active():
    # Create and soft-delete object
    obj, created = UniqueSoftDeleteModel.objects.update_or_create(name='unique-test')
    obj.delete()
    # Update it and see if it fails
    obj, created = UniqueSoftDeleteModel.objects.update_or_create(name='unique-test')
    assert obj.name == 'unique-test'
    # Settings flag is active so the revived object should be interpreted as created
    assert created == True
