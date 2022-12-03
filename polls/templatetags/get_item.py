from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    try: 
        return dictionary.get(key)
    except (AttributeError, KeyError):
        return None