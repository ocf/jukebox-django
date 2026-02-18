from pathlib import Path
import os
import tempfile

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "tmp_key")
DEBUG = False

# Data storage directory. Default to a subdirectory in the system's temp directory.
# This ensures that both the music and database are stored in a writable location.
JUKEBOX_DATA_DIR = os.environ.get("JUKEBOX_DATA_DIR", os.path.join(tempfile.gettempdir(), "jukebox-django"))
DATA_DIR = Path(JUKEBOX_DATA_DIR).resolve()

# Ensure the data directory exists
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    # During Nix builds or in restricted environments, we might not be able to create this.
    # We continue anyway as it might not be needed for the current command (e.g. collectstatic).
    pass

# Use absolute paths for music and the database to avoid ambiguity when running from different locations.
MUSIC_DIR = os.environ.get("JUKEBOX_MUSIC_DIR", str(DATA_DIR / "music"))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "termites,localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    'daphne',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jukebox',
    'django_icons',
]

ASGI_APPLICATION = 'config.asgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", BASE_DIR / "staticfiles")

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get("DJANGO_DB_PATH", str(DATA_DIR / 'db.sqlite3')),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DJANGO_ICONS = {
    "ICONS": {
        "pause": {"name": "fa-solid fa-pause"},
        "play": {"name": "fa-solid fa-play"},
        "next": {"name": "fa-solid fa-forward-step"},
        "volume": {"name": "fa-solid fa-volume-high"},
    },
}
