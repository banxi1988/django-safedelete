from django.db import models

from safedelete.tests.asserts import assert_queryset_equal
from ..models import SafeDeleteModel


class PrefetchBrother(SafeDeleteModel):
    pass


class PrefetchSister(SafeDeleteModel):
    sibling = models.ForeignKey(
        PrefetchBrother,
        related_name='sisters',
        on_delete=models.CASCADE
    )


import pytest
pytestmark = pytest.mark.django_db



def setup_function(func):
    print("setup for %r" % func)
    brother1 = PrefetchBrother.objects.create()
    brother2 = PrefetchBrother.objects.create()

    PrefetchSister.objects.create(sibling=brother1)
    PrefetchSister.objects.create(sibling=brother1)
    PrefetchSister.objects.create(sibling=brother1)
    PrefetchSister.objects.create(sibling=brother1).delete()
    PrefetchSister.objects.create(sibling=brother2)
    PrefetchSister.objects.create(sibling=brother2)
    PrefetchSister.objects.create(sibling=brother2).delete()
    PrefetchSister.objects.create(sibling=brother2).delete()

    return (brother1,brother2)

def test_prefetch_related():
    """prefetch_related() queryset should not be filtered by core_filter."""
    brothers = PrefetchBrother.objects.all().prefetch_related(
        'sisters'
    )
    for brother in brothers:
        assert_queryset_equal(
            brother.sisters.all().order_by('pk'),
            [
                repr(s) for s in PrefetchBrother.objects.get(
                    pk=brother.pk
                ).sisters.all().order_by('pk')
            ]
        )

def test_prefetch_related_is_evaluated_once(django_assert_num_queries):
    with django_assert_num_queries(2):
        brothers = PrefetchBrother.objects.all().prefetch_related('sisters')
        for brother in brothers:
            list(brother.sisters.all())
