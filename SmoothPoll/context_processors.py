from config.settings import GA_TAG
from configparser import ConfigParser


def ga_tag(request):
    return {
        "GA_TAG": GA_TAG
    }

def app_version(request):

    config = ConfigParser()
    config.read('.bumpversion.cfg')
    version = config.get('bumpversion', 'current_version')

    return {
        "APP_VERSION": version
    }

