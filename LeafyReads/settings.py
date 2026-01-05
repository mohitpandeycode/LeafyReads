
import os
from pathlib import Path
from LeafyReads.ckEditor import *
from environ import Env
import dj_database_url
env = Env()
Env.read_env()


ENVIRONMENT = env('ENVIRONMENT', default='production')


BASE_DIR = Path(__file__).resolve().parent.parent




SECRET_KEY = env('SECRET_KEY')


if ENVIRONMENT == 'development':
    DEBUG = True
    ALLOWED_HOSTS = ['*']
else:
    DEBUG = False
    ALLOWED_HOSTS = [
        "leafyreads.com",
        "www.leafyreads.com",
        "15.206.60.20",            
        "127.0.0.1",               
        "localhost",               
    ]



# Application definition

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'django_ckeditor_5',
    'home.apps.HomeConfig',
    'books.apps.BooksConfig',
    'LRAdmin.apps.LradminConfig',
    'userSection.apps.UsersectionConfig',
    'community.apps.CommunityConfig',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'debug_toolbar',
    'django.contrib.postgres',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'django_extensions',
    'django_user_agents',
    'django.contrib.sitemaps'
    
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': env('GOOGLE_CLIENT_ID', default=''),
            'secret': env('GOOGLE_CLIENT_SECRET', default=''),
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}
INTERNAL_IPS = [
    '127.0.0.1',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    
]

ROOT_URLCONF = 'LeafyReads.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':  [ BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.notifications'
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # default
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth
]


WSGI_APPLICATION = 'LeafyReads.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'LeafyReads',
#         'USER': 'postgres',
#         'PASSWORD': 'mohit@123@123', 
#         'HOST': 'localhost',
#         'PORT': '5433',
#     }
# }


DATABASE_URL = env('DATABASE_URL')
db_config = dj_database_url.config(default=DATABASE_URL, conn_max_age=0)
db_config['DISABLE_SERVER_SIDE_CURSORS'] = True
DATABASES = {
    'default': db_config
}

SESSION_COOKIE_AGE = 60 * 60 * 24 * 7


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://default:{env('REDIS_PASSWORD')}@{env('REDIS_HOST')}:{env('REDIS_PORT')}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "SSL": False,
            "SOCKET_CONNECT_TIMEOUT": 2,
            "SOCKET_TIMEOUT": 2,
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
    'UPLOAD_OPTIONS': {
        'upload_preset': 'django_auto_compress'
    }
}

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}



CKEDITOR_5_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CKEDITOR_5_UPLOAD_PATH = "uploads/ckeditor/"
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True
CKEDITOR_5_FILE_UPLOAD_PERMISSION = lambda user: user.is_staff
CKEDITOR_5_IMAGE_BACKEND = "pillow"


CSRF_TRUSTED_ORIGINS = [
    "https://leafyreads.com", 
    "https://www.leafyreads.com",
]


if ENVIRONMENT != 'development':

    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True          
    SESSION_COOKIE_SECURE = True        
    CSRF_COOKIE_SECURE = True 
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



SOCIALACCOUNT_LOGIN_ON_GET = True
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'  # where to redirect after login
LOGOUT_REDIRECT_URL = '/'  # where to redirect after logout

UNFOLD = {
    "SITE_TITLE": "LeafyReads Admin Pannel",
    "SITE_HEADER": "LeafyReads Admin",
    "SITE_SUBHEADER": "Access of all the powers",
    "THEME": "dark", 
     "SIDEBAR": {
        "show_search": True,  
        
     }
     
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR', # This will print the stack trace for 500 errors
    },
}


