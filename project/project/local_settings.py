# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1@j)kg7frpvc+-=tt@gc3hdc*q7&2qb6+@#ozc00!u12%vduk!'

AUTH_PASSWORD_VALIDATORS = []


# Drobox Api
DROPBOX_APP_KEY = 'mrcw8jglsdkv0ic'
DROPBOX_APP_SECRET = '1czbe7rq0i0eagc'
DROPBOX_APP_TYPE = 'app_folder'

DROPBOX_META_PATH = '/.meta/'
DROPBOX_PROJECTS_FILE = 'projects.txt'
DROPBOX_TAGS_FILE = 'tags.txt'

DROPBOX_DEFAULT_PROJECT = 'notebook'
DROPBOX_DEFAULT_TAG = 'tag'

SITE_PATH = 'https://light-it-07.tk/'


FOLDER_NAME_MONTH = ['jan', 'feb', 'mar', 'apr', 'may', 'june', 'july',
                     'aug', 'sept', 'oct', 'nov', 'dec']

REGEXP_FOR_MONTH_FOLDERS = '{}'.format('|'.join(FOLDER_NAME_MONTH))

REGEX_FILES = \
    '^/(?:19|20)\d\d/({})/\d\d/deez_(.*)\.txt$'.format('|'.join(FOLDER_NAME_MONTH))
