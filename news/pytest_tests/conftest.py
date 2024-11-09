from datetime import datetime, timedelta

import pytest

from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости'
    )
    return news


@pytest.fixture
def id_for_args(news):
    return (news.id,)


@pytest.fixture
def bulk_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст новости',
    )
    return comment


@pytest.fixture
def bulk_comment(author, news):
    now = timezone.now()
    # Создаём комментарии в цикле.
    for index in range(10):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
