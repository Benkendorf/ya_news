import pytest

from pytest_django.asserts import assertRedirects, assertFormError
from http import HTTPStatus

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            news_url, comment_form_data):

    client.post(news_url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author_client, news_url, comment_form_data,
                                 news, author):
    response = author_client.post(news_url, data=comment_form_data)
    assertRedirects(response, f'{news_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(news_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(comment, author_client,
                                   delete_url, comments_url):
    response = author_client.delete(delete_url)
    assertRedirects(response, comments_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  delete_url):
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, comment,
                                 edit_url, comments_url):
    response = author_client.post(edit_url, data={'text': NEW_COMMENT_TEXT})
    assertRedirects(response, comments_url)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(not_author_client, edit_url,
                                                comment):
    old_text = comment.text
    response = not_author_client.post(edit_url,
                                      data={'text': NEW_COMMENT_TEXT})

    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text
