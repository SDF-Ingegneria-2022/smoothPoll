import os
from dotenv import load_dotenv

load_dotenv()

DEBUG_CONFIGURATION = os.getenv('DEBUG_CONFIGURATION', False) == 'True'

ALLOWED_HOSTS_CONFIGURATION = os.getenv('ALLOWED_HOSTS_CONFIGURATION', []).split(',') if os.getenv('ALLOWED_HOSTS_CONFIGURATION', []).split(',')  != [''] else [] 

GA_TAG = os.getenv('GA_TAG', None) 

SITE_ID = os.getenv('SITE_ID', 0)

# main db config
USE_POSTGRESQL = os.getenv('USE_POSTGRESQL', False) == 'True'

POSTGRESQL_HOST = os.getenv('POSTGRESQL_HOST', None)
POSTGRESQL_PORT = os.getenv('POSTGRESQL_PORT', None)
POSTGRESQL_NAME = os.getenv('POSTGRESQL_NAME', None)
POSTGRESQL_USER = os.getenv('POSTGRESQL_USER', None)
POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD', None)