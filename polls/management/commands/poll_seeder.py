from django.core.management.base import BaseCommand, CommandError, CommandParser
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel

class Command(BaseCommand):
    help = 'Seed the DB with a dummy poll'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('new_polls_number', nargs='+', type=int)

        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete all polls before seeding.',
        )
    
    
    def handle(self, *args, **options):
        if options['delete']:
            PollModel.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted all polls'))
        
        new_polls_number: int = options['new_polls_number'][0]
        
        for index in range(1, new_polls_number + 1):
            try:
                new_poll: PollModel = PollModel(name=f"Poll sample name {index}", question=f"What is your favorite poll number {index}?")
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
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {new_polls_number} polls!'))