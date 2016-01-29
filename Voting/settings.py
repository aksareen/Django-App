# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#SITE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
#SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fz$_yvj)-7%!f+u6%!iix!^k(_*zy*l*n1(dce*s-9n9#-6@_y'

GOOGLESECRET_KEY = "6LcmmgwTAAAAADf47GDLp2BkRN-mttf_HREgjQhz"
GOOGLECAPTCHA_URL = "https://www.google.com/recaptcha/api/siteverify"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost','127.0.0.1']

ADMINS = (
    ('Ashish Sareen', 'ashish.sareen2013@vit.ac.in'),
)

MANAGERS = ADMINS

#CONN_MAX_AGE = 60 #None Unlimited

#CACHED DB SESSIONS 
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'rest_framework',
    #'bootstrap3',   
    #'django-user-sessions',
    'users',
    'elections',
    'datetimewidget',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    #Not needed now
    #'Voting.middleware.TimezoneMiddleware',
)

ROOT_URLCONF = 'Voting.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            #ADD CACHE.LOADER HERE 

        },
    },
]


WSGI_APPLICATION = 'Voting.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND ='django.core.mail.backends.console.EmailBackend' 
EMAIL_HOST_USER = 'varun.gambhir2012@gmail.com'
EMAIL_HOST_PASSWORD = 'GAMBHIRrocks20120210'
DEFAULT_FROM_EMAIL = 'varun.gambhir2012@gmail.com'
DEFAULT_TO_EMAIL = 'ashish.sareen2013@vit.ac.in'
EMAIL_USE_TLS = True 



SESSION_ENGINE = "django.contrib.sessions.backends.cached_db" 

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'


#Not Using Internationalisation or Localistaion Right, Now
# But I have developed the project in a way that you can easily add these 
#functionalities without re-inventing the wheel : :D

USE_I18N = False

USE_L10N = False

USE_TZ = True

AUTH_USER_MODEL = 'users.User'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    #static files for domain
    #'/var/www/static/',
)

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/users/dashboard/'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
#STATIC_ROOT = ''


# List of finder classes that know how to find static files in
# various locations.
#STATICFILES_FINDERS = (
#    'django.contrib.staticfiles.finders.FileSystemFinder',
#    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
#)

#TEMPLATE_LOADERS = (
#    'django.template.loaders.filesystem.Loader',
#    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
#)
TIMEOUT = 300

CSRF_COOKIE_NAME = 'csrf'
#need https
#CSRF_COOKIE_SECURE = False

if DEBUG:
    INTERNAL_IPS = ('127.0.0.1',)
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    INSTALLED_APPS += (
        'debug_toolbar',
    )

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }