# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'XXXX'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# Use PostgreSQL for this project
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'mydatabaseuser',
        'NAME': 'mydatabase',
    },
}