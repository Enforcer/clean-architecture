"""
Simplified settings just for testing auctions_infrastructure
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'irrelevant'
INSTALLED_APPS = [
    'auctions_infrastructure.apps.AuctionsInfrastructureConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
]

USE_TZ = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'TEST_NAME': ':memory:',
    }
}
