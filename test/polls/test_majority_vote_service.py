from typing import List
import pytest
from assertpy import assert_that
from polls.models.majority_option_model import MajorityOptionModel
from polls.models.majority_vote_model import MajorityVoteModel
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from polls.services.majority_vote_service import MajorityVoteService


@pytest.fixture()
def test_polls(request):

    dummy_poll = PollModel(name="Dummy", question="Dummy question?")
    dummy_poll.save()

    option1 = PollOptionModel(value="Valore 1", poll_fk=dummy_poll).save()

    MajorityOptionModel(rating=1, poll_option=option1).save()
    MajorityOptionModel(rating=2, poll_option=option1).save()
    MajorityOptionModel(rating=3, poll_option=option1).save()
    MajorityOptionModel(rating=4, poll_option=option1).save()
    MajorityOptionModel(rating=5, poll_option=option1).save()

    option2 = PollOptionModel(value="Valore 2", poll_fk=dummy_poll).save()

    MajorityOptionModel(rating=1, poll_option=option2).save()
    MajorityOptionModel(rating=2, poll_option=option2).save()
    MajorityOptionModel(rating=3, poll_option=option2).save()
    MajorityOptionModel(rating=4, poll_option=option2).save()
    MajorityOptionModel(rating=5, poll_option=option2).save()

    option3 = PollOptionModel(value="Valore 3", poll_fk=dummy_poll).save()

    MajorityOptionModel(rating=1, poll_option=option3).save()
    MajorityOptionModel(rating=2, poll_option=option3).save()
    MajorityOptionModel(rating=3, poll_option=option3).save()
    MajorityOptionModel(rating=4, poll_option=option3).save()
    MajorityOptionModel(rating=5, poll_option=option3).save()

    control_poll = PollModel(name="Dummy#02", question="Other dummy question?")
    control_poll.save()

    control_option1 = PollOptionModel(value="Valore 1", poll_fk=control_poll).save()

    MajorityOptionModel(rating=1, poll_option=control_option1).save()
    MajorityOptionModel(rating=2, poll_option=control_option1).save()
    MajorityOptionModel(rating=3, poll_option=control_option1).save()
    MajorityOptionModel(rating=4, poll_option=control_option1).save()
    MajorityOptionModel(rating=5, poll_option=control_option1).save()

    control_option2 = PollOptionModel(value="Valore 2", poll_fk=control_poll).save()

    MajorityOptionModel(rating=1, poll_option=control_option2).save()
    MajorityOptionModel(rating=2, poll_option=control_option2).save()
    MajorityOptionModel(rating=3, poll_option=control_option2).save()
    MajorityOptionModel(rating=4, poll_option=control_option2).save()
    MajorityOptionModel(rating=5, poll_option=control_option2).save()

    return {'voted_poll': dummy_poll, 'control_poll': control_poll}

class TestMajorityVoteService:

    @pytest.mark.django_db
    def test_majority_vote_perform_works(self, test_polls):
        """
        Test majority vote perform procedure works
        """
    
        poll: PollModel = test_polls['voted_poll']

        votes: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
                            {'poll_choice_id': poll.options()[1].id, 'rating': 4 },
                            {'poll_choice_id': poll.options()[2].id, 'rating': 5 }]

        MajorityVoteService.perform_vote(votes, poll_id=poll.id)
