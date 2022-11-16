from django.core.management.base import BaseCommand, CommandError
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel

class Command(BaseCommand):
    help = 'Seed the DB with a dummy poll'

    def handle(self, *args, **options):

        try:
            new_poll: PollModel = PollModel(name="Poll sample name", question="What is your favorite poll?")
            new_poll.save()
        except Exception as exception:
            raise CommandError('Error while creating poll: %s' % exception)
        
        try:
            new_option: PollOptionModel = PollOptionModel(key="key_1", value="Poll 1", poll_fk_id=new_poll.id)
            new_option.save()
            new_option: PollOptionModel = PollOptionModel(key="key_2", value="Poll 2", poll_fk_id=new_poll.id)
            new_option.save()
            new_option: PollOptionModel = PollOptionModel(key="key_3", value="Poll 3", poll_fk_id=new_poll.id)
            new_option.save()
        except Exception as exception:
            raise CommandError('Error while creating options: %s' % exception)
        
        self.stdout.write(self.style.SUCCESS('Successfully created poll!'))