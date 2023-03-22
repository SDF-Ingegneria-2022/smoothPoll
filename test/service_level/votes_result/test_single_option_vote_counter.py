import pytest
from typing import List
from assertpy import assert_that
from apps.polls_management.classes.poll_form_utils.poll_form import PollForm
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.services.poll_create_service import PollCreateService
from apps.polls_management.models.poll_model import PollModel
from apps.votes_results.classes.single_option_vote_counter import SingleOptionVoteCounter
from apps.votes_results.services.majority_judgment_vote_service import MajorityJudjmentVoteService



class TestSingleOptionVoteCounter:
    ## Fixtures
    @pytest.fixture
    def create_mj_poll(self, django_user_model) -> None:
        """Create votes for a majority judgment poll."""
        SINGLE_OPTION = "single_option"
        single_option_form: PollForm = PollForm({"name": "Form name", "question": "Form question", "poll_type": SINGLE_OPTION, "votable_mj": True})
        single_option_options: List[str] = ["Option 1", "Option 2", "Option 3"]
        username = "user1"
        password = "bar"
        user = django_user_model.objects.create_user(username=username, password=password)
        poll: PollModel = PollCreateService.create_or_edit_poll(single_option_form, single_option_options,user=user)
        
        return poll
    
    @pytest.fixture
    def create_votes_for_single_option_poll(self, create_mj_poll) -> None:
        """Create votes for a single option poll."""
        poll: PollModel = create_mj_poll
        
        for index in range(0, 20):
            single_option_options:  List[PollOptionModel] = poll.options()
            single_option_vote_choices: List = [{'poll_choice_id': option.id, 'rating': 1 } for option in single_option_options]
            vote = MajorityJudjmentVoteService.perform_vote(single_option_vote_choices, poll_id=str(poll.id))
        
        return poll
    
    
    @pytest.mark.django_db
    def test_count_with_twenty_vote(self, create_votes_for_single_option_poll):
        """Test count with 20 votes."""
        poll: PollModel = create_votes_for_single_option_poll
        counter: SingleOptionVoteCounter = SingleOptionVoteCounter(poll)
        
        assert_that(counter.count_majority_judgment_votes()).is_equal_to(20)
        
    @pytest.mark.django_db
    def test_count_with_no_vote(self, create_mj_poll):
        """Test count with no vote."""
        poll: PollModel = create_mj_poll
        counter: SingleOptionVoteCounter = SingleOptionVoteCounter(poll)
        
        assert_that(counter.count_majority_judgment_votes()).is_equal_to(0)
        
        