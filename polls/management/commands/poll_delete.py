from typing import Dict, Tuple
from django.core.management.base import BaseCommand
from polls.models.poll_model import PollModel


class Command(BaseCommand):
    help = 'Delete all polls from the DB.'
    
    
    def handle(self, *args, **options):
        deleted_poll: Tuple[int, Dict[str, int]] = PollModel.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_poll[0]} polls!'))