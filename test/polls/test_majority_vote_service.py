from typing import List
import pytest
from assertpy import assert_that
from polls.models.majority_judgment_model import MajorityJudgmentModel
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
    #print(dummy_poll)


    option1 = PollOptionModel(value="Valore 1", poll_fk=dummy_poll)
    option1.save()

    option2 = PollOptionModel(value="Valore 2", poll_fk=dummy_poll)
    option2.save()

    option3 = PollOptionModel(value="Valore 3", poll_fk=dummy_poll)
    option3.save()

    return {'voted_poll': dummy_poll} #'control_poll': control_poll}

class TestMajorityVoteService:

    @pytest.mark.django_db
    def test_majority_vote_perform_works(self, test_polls):
        """
        Test majority vote perform procedure works
        """

        poll: PollModel = test_polls['voted_poll']

        votes: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[2].id, 'rating': 3 }]

        MajorityVoteService.perform_vote(votes, poll_id=poll.id)

    @pytest.mark.django_db
    def test_majority_vote_result_works(self, test_polls):

        poll: PollModel = test_polls['voted_poll']
        
        votes: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[2].id, 'rating': 3 }]

        performed_vote: MajorityVoteModel = MajorityVoteService.perform_vote(votes, poll_id=poll.id)

        assert_that(performed_vote).is_instance_of(MajorityVoteModel)

        majority_judgement = MajorityJudgmentModel.objects.filter(majority_poll_vote=performed_vote.id)

        # check if we have added three votes
        # check if rating of votes is as expected
        # check if the rating are assigned to the correct options
