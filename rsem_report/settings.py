# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'log')
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
# https://docs.djangoproject.com/en/1.7/ref/settings/#secret-key
SECRET_KEY = 'es^j#4!@l$55us=^04sop)!+vczm%1(20jtu$9b(y&*9+(q_t^'

# SECURITY WARNING: don't run with debug turned on in production!
# https://docs.djangoproject.com/en/1.7/ref/settings/#debug
DEBUG = True

# https://docs.djangoproject.com/en/1.8/ref/settings/#template-debug
TEMPLATE_DEBUG = True

# https://docs.djangoproject.com/en/1.7/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.humanize',

    'rsem_report',
    'kronos',
)

# https://docs.djangoproject.com/en/1.7/ref/settings/#std:setting-MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# https://docs.djangoproject.com/en/1.7/ref/settings/#std:setting-ROOT_URLCONF
ROOT_URLCONF = 'rsem_report.urls'

# https://docs.djangoproject.com/en/1.7/ref/settings/#wsgi-application
WSGI_APPLICATION = 'rsem_report.wsgi.application'

# https://docs.djangoproject.com/en/1.7/ref/settings/#std:setting-LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s|%(asctime)s|%(name)s|%(module)s|%(process)d|%(processName)s|%(relativeCreated)d|%(thread)d|%(threadName)s|%(msecs)d ms|%(pathname)s+%(lineno)d|%(funcName)s:%(message)s'
        },
        'standard': {
            'format': '%(levelname)s|%(asctime)s|%(name)s:%(message)s'
            }
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file_rsem_report': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'rsem_report.log'),
            'formatter': 'standard'
        },
        'file_rsem_report_cron': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'rsem_report_cron.log'),
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'file_rsem_report'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'rsem_report.cron': {
            'handlers': ['console', 'file_rsem_report_cron'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'rsem_report.utils': {
            'handlers': ['console', 'file_rsem_report'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}


# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'rsem_report.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
# https://docs.djangoproject.com/en/1.7/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# https://docs.djangoproject.com/en/1.7/ref/settings/#time-zone
TIME_ZONE = 'America/Vancouver'

# https://docs.djangoproject.com/en/1.7/ref/settings/#use-i18n
USE_I18N = True

# https://docs.djangoproject.com/en/1.7/ref/settings/#use-l10n
USE_L10N = True

# https://docs.djangoproject.com/en/1.7/ref/settings/#use-tz
USE_TZ = True


# Static files (CSS, JavaScript, Images)

# https://docs.djangoproject.com/en/1.7/ref/settings/#static-url
STATIC_URL = '/static/'

# https://docs.djangoproject.com/en/1.7/ref/settings/#template-dirs
TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'),)

# https://docs.djangoproject.com/en/1.7/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
    )

# https://docs.djangoproject.com/en/1.7/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 60,
        'KEY_PREFIX': BASE_DIR
    }
}
