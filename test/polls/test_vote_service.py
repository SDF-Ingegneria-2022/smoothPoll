from polls.classes.poll_result import PollResult, PollResultVoice
from polls.models.vote_model import VoteModel
import pytest
from assertpy import assert_that
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.services.vote_service import VoteService
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException

@pytest.fixture()
def test_polls(request):

    dummy_poll = PollModel(name="Dummy", question="Dummy question?")
    dummy_poll.save()

    PollOptionModel(value="Valore 1", poll_fk=dummy_poll).save()
    PollOptionModel(value="Valore 2", poll_fk=dummy_poll).save()
    PollOptionModel(value="Valore 3", poll_fk=dummy_poll).save()

    control_poll = PollModel(name="Dummy#02", question="Other dummy question?")
    control_poll.save()

    PollOptionModel(value="Valore 1", poll_fk=control_poll).save()
    PollOptionModel(value="Valore 2", poll_fk=control_poll).save()

    return {'voted_poll': dummy_poll, 'control_poll': control_poll}
    
class TestPollService:

    @pytest.mark.django_db
    def test_vote_perform_works(self, test_polls):
        """
        Test vote perform procedure works
        """
    
        poll: PollModel = test_polls['voted_poll']

        VoteService.perform_vote(poll_id=poll.id, poll_choice_id=poll.options()[0].id)

    @pytest.mark.django_db
    def test_vote_result_works(self, test_polls):
        """
        Test the vote result procedure works
        """
        
        poll: PollModel = test_polls['voted_poll']
        result = VoteService.calculate_result(poll.id)
        assert_that(result).is_instance_of(PollResult)

        for voted_option in VoteService.calculate_result(poll.id).get_sorted_options(): 
            assert_that(voted_option).is_instance_of(PollResultVoice)


    @pytest.mark.django_db
    def test_one_vote(self, test_polls):
        """
        Test where I perform one vote and I get result
        """

        poll: PollModel = test_polls['voted_poll']

        for voted_option in VoteService.calculate_result(poll.id).get_sorted_options(): 
            assert_that(voted_option.n_votes).is_equal_to(0)

        VoteService.perform_vote(poll_id=poll.id, poll_choice_id=poll.options()[0].id)

        winner = VoteService.calculate_result(poll.id).get_sorted_options()[0]

        assert_that(winner.option.id).is_equal_to(poll.options()[0].id)
        assert_that(winner.n_votes).is_equal_to(1)

    @pytest.mark.django_db
    def test_more_votes(self, test_polls):
        """
        Test where I perform two vote for each option I get result
        """

        poll: PollModel = test_polls['voted_poll']

        for voted_option in VoteService.calculate_result(poll.id).get_sorted_options(): 
            assert_that(voted_option.n_votes).is_equal_to(0)

        VoteService.perform_vote(poll_id=poll.id, poll_choice_id=poll.options()[0].id)
        VoteService.perform_vote(poll_id=poll.id, poll_choice_id=poll.options()[1].id)
        VoteService.perform_vote(poll_id=poll.id, poll_choice_id=poll.options()[2].id)
        VoteService.perform_vote(poll_id=poll.id, poll_choice_id=poll.options()[0].id)
        VoteService.perform_vote(poll_id=poll.id, poll_choice_id=poll.options()[1].id)
        VoteService.perform_vote(poll_id=poll.id, poll_choice_id=poll.options()[2].id)

        for voted_option in VoteService.calculate_result(poll.id).get_sorted_options(): 
            assert_that(voted_option.n_votes).is_equal_to(2)

    @pytest.mark.django_db
    def test_vote_wrong_option(self, test_polls):
        """
        Test that you cannot vote an option wich doesn't exist
        """
    
        voted_poll: PollModel = test_polls['voted_poll']
        control_poll: PollModel = test_polls['control_poll']

        assert_that(VoteService.perform_vote) \
            .raises(PollOptionUnvalidException) \
            .when_called_with(poll_id=voted_poll.id,  
            poll_choice_id=control_poll.options()[0].id)

    @pytest.mark.django_db
    def test_vote_notexist_poll(self, test_polls):
        """
        Test that you cannot vote a pool wich doesn't exist
        """

        voted_poll: PollModel = test_polls['voted_poll']
        id = voted_poll.id
        option_id = voted_poll.options()[0].id
        voted_poll.delete()

        assert_that(VoteService.perform_vote) \
            .raises(PollDoesNotExistException) \
            .when_called_with(poll_id=id, poll_choice_id=option_id)

    @pytest.mark.django_db
    def test_get_results_notexistent(self, test_polls):
        """
        Test calculate results of not existent poll
        """

        voted_poll: PollModel = test_polls['voted_poll']
        id = voted_poll.id
        voted_poll.delete()

        assert_that(VoteService.calculate_result) \
            .raises(PollDoesNotExistException) \
            .when_called_with(poll_id=id)

    @pytest.mark.django_db
    def test_get_vote_by_id(self, test_polls): 
        """
        Test if I can retrieve a vote from its ID
        """

        poll: PollModel = test_polls['voted_poll']

        performed_vote = VoteService.perform_vote(poll_id=poll.id, poll_choice_id=poll.options()[0].id)
        retrieved_vote = VoteService.get_vote_by_id(vote_id=performed_vote.id)

        assert_that(retrieved_vote).is_instance_of(VoteModel)
        assert_that(retrieved_vote.id).is_equal_to(performed_vote.id)
        assert_that(retrieved_vote.poll_option).is_equal_to(performed_vote.poll_option)

    @pytest.mark.django_db
    def test_get_vote_not_exist(self, test_polls): 
        """
        Test retrieving not existing vote
        """

        poll: PollModel = test_polls['voted_poll']

        performed_vote = VoteService.perform_vote(poll_id=poll.id, poll_choice_id=poll.options()[0].id)
        id = performed_vote.id
        performed_vote.delete()

        assert_that(VoteService.get_vote_by_id) \
            .raises(VoteDoesNotExistException) \
            .when_called_with(vote_id=id)
        