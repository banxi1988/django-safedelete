import random

from django.db import models

from ..config import DELETED_VISIBLE_BY_FIELD
from ..managers import SafeDeleteManager
from ..models import SafeDeleteMixin


class OtherModel(models.Model):
    pass


class FieldManager(SafeDeleteManager):
    _safedelete_visibility = DELETED_VISIBLE_BY_FIELD


class QuerySetModel(SafeDeleteMixin):
    other = models.ForeignKey(
        OtherModel,
        on_delete=models.CASCADE
    )

    creation_date = models.DateTimeField('Created', auto_now_add=True)

    objects = FieldManager()


import pytest
pytestmark = pytest.mark.django_db

@pytest.fixture()
def other():
    return OtherModel.objects.create()

@pytest.fixture()
def instance(other):
    obj = QuerySetModel.objects.create(other=other)
    obj.delete()
    return obj

def test_select_related(instance,django_assert_num_queries):
    with django_assert_num_queries(1):
        model = QuerySetModel.objects.select_related(
            'other',
        ).get(
            pk=instance.pk
        )
        str(model.other)


def test_filter_get(instance):
    pytest.raises(
        QuerySetModel.DoesNotExist,
        QuerySetModel.objects.filter( pk=instance.pk + 1, ).get,
        pk=instance.pk
    )


def test_filter_filter(instance):
    assert QuerySetModel.objects.filter(
            pk=instance.pk + 1,
        ).filter(
            pk=instance.pk
        ).count() == 0


def test_get_field(instance):
    QuerySetModel.objects.get(
        pk=instance.pk
    )





def test_count(instance):
    assert QuerySetModel.objects.count() == 0
    assert QuerySetModel.all_objects.count() == 1

def test_iterator(instance):
    assert len(list(QuerySetModel.objects.iterator())) == 0
    assert len(list(QuerySetModel.all_objects.iterator())) == 1

def test_exists(instance):
    assert QuerySetModel.objects.filter(
            other_id=instance.other.id
        ).exists() == False

    assert QuerySetModel.all_objects.filter(
            other_id=instance.other.id
        ).exists()

def test_aggregate(instance):
    assert QuerySetModel.objects.aggregate(
            max_id=models.Max('id')
        ) == { 'max_id': None }

    assert QuerySetModel.all_objects.aggregate(
            max_id=models.Max('id')
        ) == { 'max_id': instance.id }

def test_first(instance):
    assert QuerySetModel.objects.filter(id=instance.pk).first() == None
    assert QuerySetModel.all_objects.filter(id=instance.pk).first() == instance

def test_last(instance):
    assert QuerySetModel.objects.filter(id=instance.pk).last() == None
    assert QuerySetModel.all_objects.filter(id=instance.pk).last() == instance


def test_latest(instance):
    pytest.raises(
        QuerySetModel.DoesNotExist,
        QuerySetModel.objects.filter(id=instance.pk).latest,
        'creation_date')

    assert QuerySetModel.all_objects.filter(id=instance.pk).latest('creation_date') == instance


def test_earliest(instance):
    pytest.raises(
        QuerySetModel.DoesNotExist,
        QuerySetModel.objects.filter(id=instance.pk).earliest,
        'creation_date')

    assert QuerySetModel.all_objects.filter(id=instance.pk).earliest('creation_date') == instance


def test_all(instance, other):
    amount = random.randint(1, 4)

    # Create an other object for more testing
    [QuerySetModel.objects.create(other=other).delete()
     for x in range(amount)]

    assert len(QuerySetModel.objects.all()) == 0
    assert len(QuerySetModel.all_objects.all()) == amount + 1  # Count for the already created instance


def test_all_slicing(other):
    amount = random.randint(1, 4)

    # Create an other object for more testing
    [QuerySetModel.objects.create(other=other).delete()
     for x in range(amount)]

    assert len(QuerySetModel.objects.all()[:amount]) == 0
    assert len(QuerySetModel.all_objects.all()[1:amount]) == amount - 1


def test_values_list(other):
    instance = QuerySetModel.objects.create(
        other=other
    )
    assert 1 == len(QuerySetModel.objects
            .filter(id=instance.id)
            .values_list('pk', flat=True))
    assert instance.id == QuerySetModel.objects.filter(id=instance.id).values_list('pk', flat=True)[0]
