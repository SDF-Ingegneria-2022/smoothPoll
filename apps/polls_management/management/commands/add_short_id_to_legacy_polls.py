from typing import Dict, Tuple
from django.core.management.base import BaseCommand
from apps.polls_management.classes.poll_form_utils.short_id_util import ShortIdUtil
from apps.polls_management.models.poll_model import PollModel


class Command(BaseCommand):
    help = 'Add short_id to legacy polls.'
    
    
    def handle(self, *args, **options):
        polls: Tuple[PollModel] = PollModel.objects.all()
        
        for poll in polls:
            poll.short_id = ShortIdUtil.generate()
            poll.save()
            
        self.stdout.write(self.style.SUCCESS(f'Successfully added short_id to {len(polls)} polls!'))