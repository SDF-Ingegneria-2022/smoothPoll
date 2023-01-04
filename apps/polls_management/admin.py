from .models.poll_model import PollModel
from .models.poll_option_model import PollOptionModel

from django.contrib import admin

# ----------------------------------------
# Register your models here to make them
# editable from admin panel

class PollAdmin(admin.ModelAdmin):
    pass

class PollOptionAdmin(admin.ModelAdmin):
    pass

admin.site.register(PollModel, PollAdmin)
admin.site.register(PollOptionModel, PollOptionAdmin)


