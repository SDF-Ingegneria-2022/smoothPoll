from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary[key]
    except (AttributeError, KeyError) as e:
        return None