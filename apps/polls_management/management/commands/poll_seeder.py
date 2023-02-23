from django.core.management.base import BaseCommand, CommandError, CommandParser
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel

class Command(BaseCommand):
    help = 'Seed the DB with a dummy poll'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            'new_polls_number', 
            nargs='+', 
            type=int,
            help='Number of polls to create.')

        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete all polls before seeding.',
        )

        parser.add_argument(
            '--majority',
            action='store_true',
            help='Create majority poll.',
        )
    
    
    def handle(self, *args, **options):
        if options['delete']:
            PollModel.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted all polls'))
        
        new_polls_number: int = options['new_polls_number'][0]
        
        for index in range(1, new_polls_number + 1):
            try:
                new_poll: PollModel = PollModel(name=f"Scelta di esempio NR#{index}", question=f"Che cosa si mangia sta sera?", poll_type='majority_vote')
                if options['majority']:
                    new_poll.poll_type=PollModel.PollType.MAJORITY_JUDJMENT
                    new_poll.name = "Esempio di scelta a Giudizio Maggioritario"
                new_poll.save()

            except Exception as exception:
                raise CommandError('Error while creating poll: %s' % exception)
            
            try:
                PollOptionModel(value="Pizza", poll_fk_id=new_poll.id).save()
                PollOptionModel(value="Pasta", poll_fk_id=new_poll.id).save()
                PollOptionModel(value="Carne", poll_fk_id=new_poll.id).save()
                PollOptionModel(value="Pesce", poll_fk_id=new_poll.id).save()
                PollOptionModel(value="Altro", poll_fk_id=new_poll.id).save()
            except Exception as exception:
                raise CommandError('Error while creating options: %s' % exception)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {new_polls_number} polls!'))