from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-9rzj*ngzd^4ro)7z7%!7rfqtr-^uhflh8glqpm)v@5xi99sf3@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'daphne',
    'jukebox',
    'django.contrib.staticfiles',
    'django_icons',
]

ASGI_APPLICATION = 'config.asgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DJANGO_ICONS = {
    "ICONS": {
        "pause": {"name": "fa-solid fa-pause"},
        "play": {"name": "fa-solid fa-play"},
        "next": {"name": "fa-solid fa-forward-step"},
        "volume": {"name": "fa-solid fa-volume-high"},
    },
}
