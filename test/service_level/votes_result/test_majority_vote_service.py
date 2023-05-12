from typing import List
import pytest
from assertpy import assert_that
from apps.votes_results.classes.majority_poll_result_data import MajorityPollResultData
from apps.votes_results.exceptions.majority_number_of_ratings_not_valid import MajorityNumberOfRatingsNotValid
from apps.votes_results.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from apps.polls_management.models.majority_judgment_model import MajorityJudgmentModel
from apps.polls_management.models.majority_vote_model import MajorityVoteModel
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.votes_results.services.majority_judgment_vote_service import MajorityJudjmentVoteService
from test.service_level.utils.has_test_polls import HasTestPolls


class TestMajorityVoteService(HasTestPolls):

    @pytest.mark.django_db
    def test_majority_vote_perform_works(self,test_polls):
        """
        Test majority vote perform procedure works
        """

        poll: PollModel = test_polls['voted_poll']

        votes: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[2].id, 'rating': 3 }]

        MajorityJudjmentVoteService.perform_vote(votes, poll_id=poll.id)

    @pytest.mark.django_db
    def test_majority_vote_perform_works_correctly(self, test_polls):
        """Various test to assert that the majority vote creates the vote correctly"""

        poll: PollModel = test_polls['voted_poll']
        
        votes: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[2].id, 'rating': 3 }]

        performed_vote: MajorityVoteModel = MajorityJudjmentVoteService.perform_vote(votes, poll_id=poll.id)

        assert_that(performed_vote).is_instance_of(MajorityVoteModel)

        majority_judgement = MajorityJudgmentModel.objects.filter(majority_poll_vote=performed_vote.id)

        # check if we have added three votes
        assert_that(majority_judgement.count()).is_equal_to(3)

        # check if the rating are assigned to the correct options
        assert_that(majority_judgement.get(poll_option=poll.options()[0].id).rating).is_equal_to(2)
        assert_that(majority_judgement.get(poll_option=poll.options()[1].id).rating).is_equal_to(2)
        assert_that(majority_judgement.get(poll_option=poll.options()[2].id).rating).is_equal_to(3)

    @pytest.mark.django_db
    def test_majority_vote_notexist_poll(self, test_polls):
        """
        Test that you cannot vote a majority pool which doesn't exist
        """

        votes: List[dict] = []

        voted_poll: PollModel = test_polls['voted_poll']
        id = voted_poll.id
        voted_poll.delete()

        assert_that(MajorityJudjmentVoteService.perform_vote) \
            .raises(PollDoesNotExistException) \
            .when_called_with(votes, poll_id=id)

    @pytest.mark.django_db
    def test_majority_vote_option_not_all_voted(self, test_polls):
        """
        Test that you cannot vote a majority poll when you have not selected
        a preference for every option
        """

        poll: PollModel = test_polls['voted_poll']

        votes: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[1].id, 'rating': 2 }]

        assert_that(MajorityJudjmentVoteService.perform_vote) \
            .raises(PollOptionRatingUnvalidException) \
            .when_called_with(votes, poll_id=poll.id)

    @pytest.mark.django_db
    def test_majority_vote_option_rating_number_wrong(self, test_polls):
        """
        Test that you cannot give a preference not expected by the majority poll
        (es.: 7 when the max number/value is 5)
        """

        poll: PollModel = test_polls['voted_poll']

        votes: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[1].id, 'rating': 7 },
                            {'poll_choice_id': poll.options()[2].id, 'rating': 3 }]

        assert_that(MajorityJudjmentVoteService.perform_vote) \
            .raises(MajorityNumberOfRatingsNotValid) \
            .when_called_with(votes, poll_id=poll.id)

    