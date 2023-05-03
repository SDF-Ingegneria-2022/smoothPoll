from django.template.defaulttags import register

@register.filter
def are_results_visible(poll, request):
    return poll.are_results_visible(request.user)