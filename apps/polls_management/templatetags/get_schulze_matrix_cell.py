from apps.votes_results.classes.schulze_results.i_schulze_results import ISchulzeResults
from django.template.defaulttags import register

@register.simple_tag
def get_schulze_matrix_cell(schulze_results: ISchulzeResults, a, b):
    return schulze_results.get_preference_matrix_cell(a, b)