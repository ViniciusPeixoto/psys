from datetime import datetime, timedelta, timezone

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from trees.models import Account, User


@pytest.mark.django_db
def test_newly_users_have_correct_parameters():
    alpha = User.objects.create_user(username='alpha', password='beta')
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    assert alpha.username == 'alpha'
    assert alpha.date_joined - now < timedelta(seconds=5)
    assert not alpha.is_superuser
    assert not alpha.is_staff
    assert alpha.is_active
    assert len(alpha.accounts.all()) == 0


@pytest.mark.django_db
def test_user_viewset_get(client):
    User.objects.create_user(username='alpha', password='beta')
    url = reverse('user-list')

    response = client.get(url)

    assert response.status_code == 200
    assert len(response.json()) == 1
    user = response.json().pop()
    assert user.get('username') == 'alpha'


@pytest.mark.django_db
def test_user_viewset_unauthorized(client):
    data = {'username': 'alpha'}
    url = reverse('user-list')

    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_viewset_post(client, django_user_model):
    username = 'test_user'
    password = 'test_password'
    user = django_user_model.objects.create(
        username=username, password=password
    )
    one = Account.objects.create(name='one')
    data = {'username': 'alpha', 'password': 'beta', 'accounts': [one.id]}
    url = reverse('user-list')
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    client.force_login(user)
    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 201
    assert response.json().get('username') == 'alpha'
    assert response.json().get('password') is None

    joined = datetime.strptime(
        response.json().get('date_joined'), '%Y-%m-%dT%H:%M:%S.%f%z'
    )
    assert joined - now < timedelta(seconds=5)


@pytest.mark.django_db
def test_user_viewset_patch(client, django_user_model):
    username = 'test_user'
    password = 'test_password'
    user = django_user_model.objects.create(
        username=username, password=password
    )
    alpha = User.objects.create_user(username='alpha', password='beta')
    data = {'username': 'beta', 'is_active': False}
    url = reverse('user-detail', args=[alpha.id])

    client.force_login(user)
    response = client.patch(url, data=data, content_type='application/json')

    assert response.status_code == 200

    assert response.json().get('username') == 'beta'
    joined = datetime.strptime(
        response.json().get('date_joined'), '%Y-%m-%dT%H:%M:%S.%f%z'
    )
    assert joined == alpha.date_joined
    assert response.json().get('is_superuser') is False
    assert response.json().get('is_staff') is False
    assert response.json().get('is_active') is False


@pytest.mark.django_db
def test_user_viewset_delete(client, django_user_model):
    username = 'test_user'
    password = 'test_password'
    user = django_user_model.objects.create(
        username=username, password=password
    )
    alpha = User.objects.create_user(username='alpha', password='beta')
    url = reverse('user-detail', args=[alpha.id])

    client.force_login(user)
    response = client.delete(url)

    assert response.status_code == 204
    with pytest.raises(ObjectDoesNotExist):
        User.objects.get(username='alpha')
