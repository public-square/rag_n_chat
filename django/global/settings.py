"""
Django settings configuration for the Rag N Chat API project.

Key Settings:
- DEBUG: Set to True for development (should be False in production)
- INSTALLED_APPS: Includes Django REST framework and custom 'api' app
- REST_FRAMEWORK: Configured to use JSONRenderer by default
- DATABASE: Uses SQLite3 for development
- ALLOWED_HOSTS: Empty list (configure for production)
- SECRET_KEY: Development key (should be changed in production)

Security Notes:
- Debug mode should be disabled in production
- Secret key should be changed and stored securely in production
- Allowed hosts should be configured for production deployment
- Uses Django's built-in security middleware

API Configuration:
- Uses Django REST framework for API functionality
- Accepts and returns JSON data only
- No authentication required (add if needed)
"""

from pathlib import Path
import environ
import os

# Initialize environ
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, 'global', '.env'))

# Server configuration
API_SERVER_PORT = env('API_SERVER_PORT')
SECRET_KEY = env('DJANGO_SECRET_KEY')

# GitHub configuration
GITHUB_CLONE_DIR = os.path.expanduser(env('GITHUB_CLONE_DIR'))
GITHUB_TOKEN = env('GITHUB_TOKEN', default='')

# OpenAI configuration
OPENAI_API_KEY = env('OPENAI_API_KEY')

# Pinecone additional settings
PINECONE_ENVIRONMENT = env('PINECONE_ENVIRONMENT')
PINECONE_API_KEY = env('PINECONE_API_KEY')
PINECONE_INDEX = env('PINECONE_INDEX')
EMBEDDING_DIMENSIONS = env('EMBEDDING_DIMENSIONS')

# LangChain configuration
LANGCHAIN_TRACING_V2 = env('LANGCHAIN_TRACING_V2')
LANGCHAIN_ENDPOINT = env('LANGCHAIN_ENDPOINT')
LANGCHAIN_API_KEY = env('LANGCHAIN_API_KEY')
LANGCHAIN_PROJECT = env('LANGCHAIN_PROJECT')

# Tavily configuration
TAVILY_API_KEY = env('TAVILY_API_KEY')


# Django settings
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'global.urls'

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

WSGI_APPLICATION = 'global.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}
