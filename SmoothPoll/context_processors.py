from config.settings import GA_TAG

def ga_tag(request):
    return {
        "GA_TAG": GA_TAG
    }

