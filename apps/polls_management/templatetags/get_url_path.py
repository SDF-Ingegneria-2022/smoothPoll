from django.template.defaulttags import register

@register.filter
def get_url_path(url: str) -> str:
    return url.split("/")[1]