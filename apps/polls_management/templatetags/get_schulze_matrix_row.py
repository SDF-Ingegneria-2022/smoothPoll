from apps.votes_results.classes.schulze_results.i_schulze_results import ISchulzeResults
from django.template.defaulttags import register

@register.filter
def get_schulze_matrix_row(schulze_results: ISchulzeResults, option):
    return schulze_results.get_preference_matrix_row(option)