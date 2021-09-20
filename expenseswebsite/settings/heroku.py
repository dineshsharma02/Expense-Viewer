"""
Production Settings for Heroku
"""

import environ

# If using in your own project, update the project namespace below
from expenseswebsite.settings.base import *

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
# False if not in os.environ
DEBUG = env('DEBUG')
# DEBUG = False
# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Parse database connection url strings like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    'default': env.db(),
}

EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER')
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')


# EMAIL_HOST = os.environ.get('EMAIL_HOST')
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
# EMAIL_USE_TLS = True
# DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER')
# EMAIL_PORT = 587
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')