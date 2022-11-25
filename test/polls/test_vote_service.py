from polls.classes.poll_result import PollResult, PollResultVoice
from polls.models.vote_model import VoteModel
import pytest
from assertpy import assert_that
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.services.vote_service import VoteService

@pytest.fixture()
def test_polls(request):

    dummy_poll = PollModel(name="Dummy", question="Dummy question?")
    dummy_poll.save()

    PollOptionModel(key="1", value="Valore 1", poll_fk=dummy_poll).save()
    PollOptionModel(key="2", value="Valore 2", poll_fk=dummy_poll).save()
    PollOptionModel(key="3", value="Valore 3", poll_fk=dummy_poll).save()

    def teardown():
        dummy_poll.delete()
    request.addfinalizer(teardown)

    return {'voted_poll': dummy_poll}
    
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

    




        
