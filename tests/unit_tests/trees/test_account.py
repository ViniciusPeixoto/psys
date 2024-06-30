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
    url = reverse('account-list')

    response = client.get(url)

    assert response.status_code == 200
    assert len(response.json()) == 2
    accounts = response.json()
    assert all(
        account.get('name') in ['Gods', 'Humans'] for account in accounts
    )


@pytest.mark.django_db
def test_account_viewset_unauthorized(client):
    data = {'name': 'alpha', 'active': True}
    url = reverse('account-list')

    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 403


@pytest.mark.django_db
def test_account_viewset_post(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
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
def test_account_viewset_patch(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    alpha = Account.objects.get(name='Gods')
    data = {'name': 'beta', 'active': False}
    url = reverse('account-detail', args=[alpha.id])
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    client.force_login(user)
    response = client.patch(url, data=data, content_type='application/json')

    assert response.status_code == 200
    assert response.json().get('name') == 'beta'
    assert response.json().get('active') is False

    created = datetime.strptime(
        response.json().get('created'), '%Y-%m-%dT%H:%M:%S.%f%z'
    )
    assert created - now < timedelta(seconds=5)


@pytest.mark.django_db
def test_account_viewset_delete(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    alpha = Account.objects.get(name='Gods')
    url = reverse('account-detail', args=[alpha.id])

    client.force_login(user)
    response = client.delete(url)

    assert response.status_code == 204
    with pytest.raises(ObjectDoesNotExist):
        Account.objects.get(id=alpha.id)
