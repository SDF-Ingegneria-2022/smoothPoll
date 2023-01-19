import os
from dotenv import load_dotenv

load_dotenv()

DEBUG_CONFIGURATION = os.getenv('DEBUG_CONFIGURATION', False) == 'True'

ALLOWED_HOSTS_CONFIGURATION = os.getenv('ALLOWED_HOSTS_CONFIGURATION', []).split(',') if os.getenv('ALLOWED_HOSTS_CONFIGURATION', []).split(',')  != [''] else [] 

GA_TAG = os.getenv('GA_TAG', None) 

SITE_ID = os.getenv('SITE_ID', None)