# Django settings for aaltoplus project.
import os
import conf

# Lines for Celery.
import djcelery
djcelery.setup_loader()

# Returns the path to given filename
def get_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
#gist middleware variables
XS_SHARING_ALLOWED_ORIGINS = ['http://algoviz-beta6.cc.vt.edu','http://algoviz.org','http://algoviz-beta7.cc.vt.edu']
XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ["Content-Type"] 
File_Path = "/home/OpenDSA-server/ODSA-django/openpop/build/"

APPEND_SLASH=True

ACCOUNT_ACTIVATION_DAYS = 365 

#celery broker
#BROKER_URL = 'amqp://guest:guest@localhost:5672/'
BROKER_URL = "django://" 
 
# This URL is used when building absolute URLs to this service
BASE_URL = ""

ADMINS = (
     ('', ''),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': conf.name,         #g3et_path('test.db'),            # Or path to database file if using sqlite3.
        'USER': conf.user,                  # Not used with sqlite3. dbadmin
        'PASSWORD': conf.password,                  # Not used with sqlite3. vis4_dsa
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name

# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/var/www/media/'   #get_path("media/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = get_path("static/")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    "/home/efouh/OpenDSA-server/ODSA-django/assets/",
    #"/home/aalto/aaltoplus/assets"
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = conf.secret_key 

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader', # Replace 'Loader' with 'load_template_source' if Django version is < 1.4.1
    'django.template.loaders.app_directories.Loader', # Replace 'Loader' with 'load_template_source' if Django version is < 1.4.1
#     'django.template.loaders.eggs.load_template_source',
)

# Cache backends
CACHES = {
    #'default': {
    #    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    #    'LOCATION': 'django_db_cache',
    #}
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'userprofile.middleware.StudentGroupMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'lib.middleware.SqlInjectionMiddleware',
    'middleware.django-crossdomainxhr-middleware.XsSharing',
    'django_user_agents.middleware.UserAgentMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "userprofile.context_processors.student_group",
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    get_path('templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

#STATICFILES_DIRS = (
#    get_path("assets"),
#)

INSTALLED_APPS = (
    'oauth_provider',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.humanize', 
    'exercise',
    'course',
    #'south', # South disabled due to refactoring of the database 
    'inheritance',
    'tastypie',
    'userprofile',
    'apps',
    'opendsa',
    'registration',
    'kombu.transport.django',
    'djcelery',
    'django_user_agents',
)

# OAuth settings
OAUTH_AUTHORIZE_VIEW = 'oauth_provider.custom_views.oauth_authorize'

LOGIN_REDIRECT_URL = "/"

AUTH_PROFILE_MODULE = 'userprofile.UserProfile'

FILE_UPLOAD_HANDLERS = (
                        #"django.core.files.uploadhandler.MemoryFileUploadHandler",
                        "django.core.files.uploadhandler.TemporaryFileUploadHandler",
                        )


# Shibboleth settings
SHIB_ATTRIBUTE_MAP = {
    "HTTP_SHIB_IDENTITY_PROVIDER": (True, "idp"),
    "HTTP_SHIB_SHARED_TOKEN": (False, "shared_token"),
    "HTTP_EPPN": (True, "eppn"),
    "HTTP_SHIB_CN": (False, "cn"),
    "HTTP_REMOTE_USER": (False, "email"),
    "HTTP_SHIB_GIVENNAME": (False, "first_name"),
    "HTTP_SHIB_SN": (False, "last_name"),
}
SHIB_USERNAME = "eppn"
SHIB_EMAIL = "email"

#EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Host for sending e-mail.
EMAIL_HOST = 'opendsa.cc.vt.edu'

# Port for sending e-mail.
EMAIL_PORT = 587

# Optional SMTP authentication information for EMAIL_HOST.
DEFAULT_FROM_EMAIL = 'opendsa.cc.vt.edu <noreply@opendsa.cc.vt.edu>'
EMAIL_HOST_USER = 'root'
EMAIL_HOST_PASSWORD = '' 
EMAIL_USE_TLS = True

