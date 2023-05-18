from typing import List
import pytest
from assertpy import assert_that
from apps.polls_management.classes.poll_form_utils.poll_form import PollForm
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_option_number_mismatch_exception import PollOptionNumberMismatch
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.schulze_vote_model import SchulzeVoteModel
from apps.polls_management.services.poll_create_service import PollCreateService
from apps.votes_results.services.schulze_method_vote_service import SchulzeMethodVoteService
from apps.votes_results.views.vote.schulze_method_vote_view import SchulzeMethodVoteView



class TestSchulzeVoteService():
    ## Fixtures
    @pytest.fixture
    def create_schulze_poll(self, django_user_model) ->None:
        SCHULZE = "schulze"
        schulze_method_form: PollForm = PollForm({"name": "Form name", "question": "Form question", "poll_type": SCHULZE, "votable_mj": True})
        schulze_options: List[str] = ["Option 1", "Option 2", "Option 3"]
        username = "user1"
        password = "bar"
        user = django_user_model.objects.create_user(username=username, password=password)
        poll: PollModel = PollCreateService.create_or_edit_poll(schulze_method_form, schulze_options,user=user)
        return poll

    #def create_schulze_user_order(self, django_user_model):


    @pytest.mark.django_db
    def test_schulze_vote_perform_works(self,create_schulze_poll):
        """
        Test schulze vote perform procedure works
        """

        poll: PollModel = create_schulze_poll
        schulze_options:  List[PollOptionModel] = poll.options()
        votes: List[int] = [option.id for option in schulze_options]

        SchulzeMethodVoteService.perform_vote(votes, poll_id=poll.id)

    @pytest.mark.django_db
    def test_schulze_vote_istance(self, create_schulze_poll):
        """Various test to assert that the schulze vote creates the vote correctly"""

        poll: PollModel = create_schulze_poll
        schulze_options:  List[PollOptionModel] = poll.options()
        votes: List[int] = [option.id for option in schulze_options]
        SchulzeMethodVoteService.perform_vote(votes, poll_id=poll.id)
        performed_vote: SchulzeVoteModel = SchulzeMethodVoteService.perform_vote(votes, poll_id=poll.id)

        assert_that(performed_vote).is_instance_of(SchulzeVoteModel)


    #da mettere a posto
    @pytest.mark.django_db
    def test_schulze_vote_perform_order(self, create_schulze_poll):
        """Various test to assert that the schulze vote creates the vote correctly"""

        poll: PollModel = create_schulze_poll
        schulze_options:  List[PollOptionModel] = poll.options()
        option_id: List[int] = [option.id for option in schulze_options]
        performed_vote: SchulzeVoteModel = SchulzeMethodVoteService.perform_vote(option_id, poll_id=poll.id)
        vote_order: List[int] = performed_vote.get_order_as_ids()
        #need to cast to int
        for index,vote in enumerate(vote_order):
            assert_that(option_id[index]).is_equal_to(int(vote))

    @pytest.mark.django_db
    def test_schulze_vote_notexist_poll(self, create_schulze_poll):
        """
        Test that you cannot vote a schulze pool which doesn't exist
        """
        poll: PollModel = create_schulze_poll
        schulze_options:  List[PollOptionModel] = poll.options()
        votes: List[int] = [option.id for option in schulze_options]
        id = poll.id
        poll.delete()

        assert_that(SchulzeMethodVoteService.perform_vote) \
            .raises(PollDoesNotExistException) \
            .when_called_with(votes, poll_id=id)

    @pytest.mark.django_db
    def test_schulze_vote_option_voted_number_wrong(self, create_schulze_poll):
        """
        Option order by client > option of the poll
        """
        poll: PollModel = create_schulze_poll
        schulze_options:  List[PollOptionModel] = poll.options()
        votes: List[int] = [option.id for option in schulze_options]
        #append another vote 
        votes.append(1)
        id = poll.id

        assert_that(SchulzeMethodVoteService.perform_vote) \
            .raises(PollOptionNumberMismatch) \
            .when_called_with(votes, poll_id=id)
