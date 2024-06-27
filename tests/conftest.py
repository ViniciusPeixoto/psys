import pytest
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test_db',
        'ATOMIC_REQUESTS': True,
    }
