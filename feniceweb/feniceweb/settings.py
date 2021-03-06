"""
Django settings for feniceweb project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

from machina import MACHINA_MAIN_TEMPLATE_DIR
from machina import MACHINA_MAIN_STATIC_DIR

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_DIR = os.path.dirname(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [ 'localhost', '127.0.0.1' ]

INTERNAL_IPS = (
    '127.0.0.1',
)

# Application definition

INSTALLED_APPS = [
    "feniceerrors.apps.FeniceerrorsConfig",
    "feniceauth.apps.FeniceauthConfig",
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.sites',  # Required for django-helpdesk
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.humanize',  # Required for django-helpdesk
    'django_extensions',
    'django_ace',
    'ckeditor',
    'ckeditor_uploader',
    'avatar',

    # django-helpdesk dependencies
    #'markdown_deux',  # Required for Knowledgebase item formatting
    'bootstrapform',  # Required for nicer formatting of forms with the default templates
    #'helpdesk',       # This is us!

    # Machina dependencies:
    'mptt',
    'haystack',
    'widget_tweaks',

    # Machina apps:
    'machina',
    'machina.apps.forum',
    'machina.apps.forum_conversation',
    'machina.apps.forum_conversation.forum_attachments',
    'machina.apps.forum_conversation.forum_polls',
    'machina.apps.forum_feeds',
    'machina.apps.forum_moderation',
    'machina.apps.forum_search',
    'machina.apps.forum_tracking',
    'machina.apps.forum_member',
    'machina.apps.forum_permission',

    # Pinax
    "pinax.badges",
    #"pinax.announcements",
    "pinax.calendars",
    #"pinax.likes",
    #"pinax.messages",

    "fenicemisc.apps.FenicemiscConfig",
    "fenicegdpr.apps.FenicegdprConfig",
    "fenicestat.apps.FenicestatConfig",
    "feniceblog.apps.FeniceblogConfig",

]

SITE_ID = 1

AUTH_USER_MODEL = 'feniceauth.User'

LOGIN_URL = "/accounts/login/"

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    #'pinax.likes.auth_backends.CanLikeBackend',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    #'django.contrib.sessions.middleware.SessionMiddleware',
    'fenicemisc.middleware.FeniceSessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'fenicemisc.middleware.SaveBrowserDataContextMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "feniceerrors.middleware.ErrorHandlingMiddleware",
    'crum.CurrentRequestUserMiddleware',
    'machina.apps.forum_permission.middleware.ForumPermissionMiddleware',
]

ROOT_URLCONF = 'feniceweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ 
            os.path.join(BASE_DIR,"templates"),
            MACHINA_MAIN_TEMPLATE_DIR,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'fenicemisc.context_processors.community',
                'machina.core.context_processors.metadata',
            ],
            # 'loaders': [
            #     'django.template.loaders.filesystem.Loader',
            #     'django.template.loaders.app_directories.Loader',
            # ]
        },
    },
]

WSGI_APPLICATION = 'feniceweb.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        #'ENGINE': 'django.db.backends.postgresql',    # Add 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        'NAME': 'fenice-devel',      # Or path to database file if using sqlite3.
        'USER': 'fenice-devel',      # Not used with sqlite3.
        'PASSWORD': 'fenice-devel',  # Not used with sqlite3.
        'HOST': '',              # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',              # Set to empty string for default. Not used with sqlite3.

    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

### Cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'machina_attachments': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp',
    },
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'it'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PARENT_DIR,"web","static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    MACHINA_MAIN_STATIC_DIR,
]

FIXTURE_DIRS = [
    os.path.join(BASE_DIR, "fixtures"),
]

MEDIA_ROOT = os.path.join(BASE_DIR,"media")
MEDIA_URL = "/media/"


### Haystack/Machina
# You can also decide to use a more powerfull backend such as Solr or Whoosh:
# https://django-machina.readthedocs.io/en/latest/getting_started.html

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

MACHINA_MARKUP_LANGUAGE = None
MACHINA_MARKUP_WIDGET = 'ckeditor.widgets.CKEditorWidget'

MACHINA_PROFILE_AVATARS_ENABLED = False

### Avatar

AVATAR_THUMB_FORMAT = "PNG"
AVATAR_AUTO_GENERATE_SIZES = [80,128]

## django-registration
ACCOUNT_ACTIVATION_DAYS = 3

## django-ckeditor

# relative to MEDIA_ROOT
CKEDITOR_UPLOAD_PATH = "ckeditor_uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_RESTRICT_BY_DATE = True

CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono',
        # 'skin': 'office2013',
        'toolbar': 'Fenice',  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        'height': 400,
        'width': '100%',
        'filebrowserWindowHeight': 725,
        'filebrowserWindowWidth': 940,
        # 'toolbarCanCollapse': True,
        # 'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage', # the upload image feature
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            # 'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath',
            'emojione', # not in django-ckeditor
        ]),
        'smiley_path': '/static/ckeditor/ckeditor/plugins/smiley/images/',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_Fenice': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 
                                           #'NewPage', 
                                           'Preview','Maximize','ShowBlocks']}, 
                                           #'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            #{'name': 'forms',
            # 'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
            #           'HiddenField']},
            '/',
            {'name': 'basicstyles',
             'items': ['FontSize','Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript','TextColor', 'BGColor', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['Format','NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',]},
                       #'Language']},
            '/',
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', #'Flash', 
                       'Table', 'HorizontalRule', 'Smiley','Emojione', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            #{'name': 'styles', 'items': ['Styles', 'Format', 
                                         #'Font', 
            #                             'FontSize']},
            {'name': 'tools', 'items': []},
            #{'name': 'about', 'items': ['About']},
            # '/',  # put this to force next toolbar on new line
            # {'name': 'yourcustomtools', 'items': [
            #     # put the name of your editor.ui.addButton here
            #     'Preview',
            #     'Maximize',
            # ]},
        ],
    },
}

### Pinax

PINAX_LIKES_LIKABLE_MODELS = {
    "app.Model": {}  # override default config settings for each model in this dict
}


## Fenice

CSRF_FAILURE_VIEW = 'feniceerrors.views.csrf_failure'

COMMUNITY_NAME = "Costruttori di Mondi"
COMMUNITY_SLOGAN = "Slogan"
COMMUNITY_DESCRIPTION = "Costruttori di Mondi"

CREDITS_THUMBNAILS_DIR = os.path.join(BASE_DIR, "static", "images", "credits", "thumbnails")
CREDITS_THUMBNAILS_CONTEXT = os.path.join( "/static", "images", "credits", "thumbnails")

AGREEMENT_NAMES = {
    "coming-soon": "Coming Soon",
}


try:
    from .local_settings import *
except ImportError:
    raise Exception("A local_settings.py file is required to run this project")
