# coding: utf-8
import pytest
from typing import NamedTuple, Optional
from safedelete.models import SafeDeleteModel
from ..config import HARD_DELETE, SOFT_DELETE

__author__ = '代码会说话'

class ExpectedCount(NamedTuple):
  all:int
  all_with_deleted:int

class ExpectedResults(NamedTuple):
  before_delete:ExpectedCount
  after_delete:ExpectedCount
  after_save:Optional[ExpectedCount] = None


def assert_delete(instance:SafeDeleteModel, expected_results:ExpectedResults, force_policy:Optional[int]=None, save=True):
  """Assert specific specific expected results before delete, after delete and after save.

  Example of expected_results, see SafeDeleteTestCase.assertSoftDelete.

  Args:
      instance: Model instance.
      expected_results: Specific expected results before delete, after delete and after save.
      force_policy: Specific policy to force, None if no policy forced. (default: {None})
      save: Whether to test the Model.save() restoration. (default: {True})
  """
  model = instance.__class__

  assert model.objects.count() == expected_results.before_delete.all
  assert model.all_objects.count() == expected_results.before_delete.all_with_deleted

  if force_policy is not None:
    instance.delete(force_policy=force_policy)
  else:
    instance.delete()

  assert model.objects.count() == expected_results.after_delete.all
  assert model.all_objects.count() == expected_results.after_delete.all_with_deleted

  if not save:
    return

  # If there is no after_save in the expected results, then we assume
  # that Model.save will give a DoesNotExist exception because it was
  # a hard delete. So we test whether it was a hard delete.
  if expected_results.after_save:
    instance.save()
    assert    model.objects.count() == expected_results.after_save.all
    assert model.all_objects.count() == expected_results.after_save.all_with_deleted
  else:
    pytest.raises(model.DoesNotExist, instance.refresh_from_db )

def assert_soft_delete(instance:SafeDeleteModel, force=False, **kwargs):
  """Assert whether the given model instance can be soft deleted.

  Args:
      instance: Model instance.
      force: Whether to force the soft delete policy. (default: {False})
  """
  # Saving a soft deleted model should reinstate it.
  expected_results=ExpectedResults(
    before_delete=ExpectedCount(all=1,all_with_deleted=1),
    after_delete=ExpectedCount(all=0,all_with_deleted=1),
    after_save=ExpectedCount(all=1,all_with_deleted=1)
  )
  force_policy = SOFT_DELETE if force else None
  assert_delete(instance,expected_results=expected_results,force_policy=force_policy, **kwargs)


def assert_hard_delete(instance:SafeDeleteModel, force=False, **kwargs):
  """Assert whether the given model instance can be hard deleted.

  Args:
      instance: Model instance.
      force: Whether to force the soft delete policy. (default: {False})
  """
  # Saving a soft deleted model should reinstate it.
  expected_results=ExpectedResults(
    before_delete=ExpectedCount(all=1,all_with_deleted=1),
    after_delete=ExpectedCount(all=0,all_with_deleted=0),
  )
  force_policy = HARD_DELETE if force else None
  assert_delete(instance,expected_results=expected_results,force_policy=force_policy, **kwargs)
