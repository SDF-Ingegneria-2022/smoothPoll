from apps.polls_management.models.poll_token import PollTokens
from .models.poll_model import PollModel
from .models.poll_option_model import PollOptionModel
from .models.vote_model import VoteModel
from .models.majority_vote_model import MajorityVoteModel, MajorityJudgmentModel

from django.contrib import admin

# Register your models here to make them
# editable from admin panel

# ----------------------------------------
# polls management models

class PollAdmin(admin.ModelAdmin):
    pass

class PollOptionAdmin(admin.ModelAdmin):
    pass

class PollTokenAdmin(admin.ModelAdmin):
    pass

admin.site.register(PollModel, PollAdmin)
admin.site.register(PollOptionModel, PollOptionAdmin)
admin.site.register(PollTokens, PollTokenAdmin)

# ----------------------------------------
# vote models

class SingleOptionVoteAdmin(admin.ModelAdmin):
    pass

class MajorityJudgmentVoteAdmin(admin.ModelAdmin):
    pass

class MajorityJudgmentJudgmentAdmin(admin.ModelAdmin):
    pass

admin.site.register(VoteModel, SingleOptionVoteAdmin)
admin.site.register(MajorityVoteModel, MajorityJudgmentVoteAdmin)
admin.site.register(MajorityJudgmentModel, MajorityJudgmentJudgmentAdmin)

# TODO: give models more significative "__str__()" method 
# (so admin panel is more readable)
