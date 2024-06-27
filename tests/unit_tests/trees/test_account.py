from datetime import datetime, timedelta, timezone

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from trees.models import Account


@pytest.mark.django_db
def test_newly_accounts_have_correct_parameters():
    alpha = Account.objects.create(name='alpha')
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    assert alpha.name == 'alpha'
    assert alpha.active is True
    assert alpha.created - now < timedelta(seconds=5)


@pytest.mark.django_db
def test_account_viewset_get(client):
    Account.objects.create(name='alpha')
    url = reverse('account-list')

    response = client.get(url)

    assert response.status_code == 200
    assert len(response.json()) == 1
    account = response.json().pop()
    assert account.get('name') == 'alpha'


@pytest.mark.django_db
def test_account_viewset_unauthorized(client):
    data = {'name': 'alpha', 'active': True}
    url = reverse('account-list')

    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 403


@pytest.mark.django_db
def test_account_viewset_post(client, django_user_model):
    username = 'test_user'
    password = 'test_password'
    user = django_user_model.objects.create(
        username=username, password=password
    )
    data = {'name': 'alpha', 'active': True}
    url = reverse('account-list')
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    client.force_login(user)
    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 201
    assert response.json().get('name') == 'alpha'
    assert response.json().get('active') is True

    created = datetime.strptime(
        response.json().get('created'), '%Y-%m-%dT%H:%M:%S.%f%z'
    )
    assert created - now < timedelta(seconds=5)


@pytest.mark.django_db
def test_account_viewset_put(client, django_user_model):
    username = 'test_user'
    password = 'test_password'
    user = django_user_model.objects.create(
        username=username, password=password
    )
    alpha = Account.objects.create(name='alpha')
    data = {'name': 'beta', 'active': False}
    url = reverse('account-detail', args=[alpha.id])
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    client.force_login(user)
    response = client.put(url, data=data, content_type='application/json')

    assert response.status_code == 200
    assert response.json().get('name') == 'beta'
    assert response.json().get('active') is False

    created = datetime.strptime(
        response.json().get('created'), '%Y-%m-%dT%H:%M:%S.%f%z'
    )
    assert created - now < timedelta(seconds=5)


@pytest.mark.django_db
def test_account_viewset_delete(client, django_user_model):
    username = 'test_user'
    password = 'test_password'
    user = django_user_model.objects.create(
        username=username, password=password
    )
    alpha = Account.objects.create(name='alpha')
    url = reverse('account-detail', args=[alpha.id])

    client.force_login(user)
    response = client.delete(url)

    assert response.status_code == 204
    with pytest.raises(ObjectDoesNotExist):
        Account.objects.get(name='alpha')
