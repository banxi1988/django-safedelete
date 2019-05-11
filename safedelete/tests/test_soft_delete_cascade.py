from django.db import models
from safedelete import SOFT_DELETE_CASCADE, SOFT_DELETE
from safedelete.models import SafeDeleteModel
from safedelete.tests.models import Article, Author, Category

from unittest.mock import patch
import pytest
pytestmark = pytest.mark.django_db

class Press(SafeDeleteModel):
    name = models.CharField(max_length=200)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class PressNormalModel(models.Model):
    name = models.CharField(max_length=200)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class CustomAbstractModel(SafeDeleteModel):

    class Meta:
        abstract = True


class ArticleView(CustomAbstractModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    article = models.ForeignKey(Article, on_delete=models.CASCADE)

@pytest.fixture()
def authors():
    return (
      Author.objects.create(),
      Author.objects.create(),
      Author.objects.create(),
    )

@pytest.fixture()
def categories():
    return (
    Category.objects.create(name='category 0'),
    Category.objects.create(name='category 1'),
    Category.objects.create(name='category 2'),
    )

@pytest.fixture()
def articles(authors,categories):
    return (
    Article.objects.create(author=authors[1]),
    Article.objects.create(author=authors[1], category=categories[1]),
    Article.objects.create(author=authors[2], category=categories[2]),
    )

@pytest.fixture()
def press(articles):
    return Press.objects.create(name='press 0', article=articles[2])


def test_soft_delete_cascade(authors,categories,articles,press):
    assert Author.objects.count()== 3
    assert Article.objects.count() == 3
    assert Category.objects.count() == 3
    assert Press.objects.count() == 1

    authors[2].delete(force_policy=SOFT_DELETE_CASCADE)

    assert Author.objects.count() == 2
    assert Author.all_objects.count() == 3
    assert Article.objects.count() == 2
    assert Article.all_objects.count() == 3
    assert Press.objects.count() == 0
    assert Press.all_objects.count() == 1


def test_soft_delete_cascade_with_normal_model(authors,categories,articles,press):
    PressNormalModel.objects.create(name='press 0', article=articles[2])
    authors[2].delete(force_policy=SOFT_DELETE_CASCADE)

    assert PressNormalModel.objects.count() == 1

    assert  Author.objects.count() == 2
    assert Author.all_objects.count() ==  3
    assert Article.objects.count() ==  2
    assert Article.all_objects.count() ==  3
    assert Press.objects.count() ==  0
    assert Press.all_objects.count() ==  1


def test_soft_delete_cascade_with_abstract_model(authors,categories,articles,press):
    ArticleView.objects.create(article=articles[2])

    articles[2].delete(force_policy=SOFT_DELETE_CASCADE)

    assert Article.objects.count() ==  2
    assert Article.all_objects.count() ==  3

    assert ArticleView.objects.count() ==  0
    assert ArticleView.all_objects.count() ==  1

def test_soft_delete_cascade_deleted(authors,categories,articles,press):
    articles[0].delete(force_policy=SOFT_DELETE)
    assert authors[1].article_set.count() ==  1

    with patch('safedelete.tests.models.Article.delete') as delete_article_mock:
        authors[1].delete(force_policy=SOFT_DELETE_CASCADE)
        # delete_article_mock.assert_called_once doesn't work on py35
        assert delete_article_mock.call_count ==  1


def test_undelete_with_soft_delete_cascade_policy(authors,categories,articles,press):
    authors[2].delete(force_policy=SOFT_DELETE_CASCADE)
    authors[2].undelete(force_policy=SOFT_DELETE_CASCADE)

    assert Author.objects.count() ==  3
    assert Article.objects.count() ==  3
    assert Category.objects.count() ==  3
    assert Press.objects.count() ==  1
