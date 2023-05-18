from typing import List
import pytest
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.schulze_vote_model import SchulzeVoteModel
from apps.votes_results.classes.schulze_results.schulze_results_adapter import SchulzeResultsAdapter
from test.service_level.utils.has_test_polls import HasTestPolls
from assertpy import assert_that


class TestSchulzeResultsAdapter(HasTestPolls):

    # check schulze results adapter class ----------------------------------------------

    @pytest.mark.django_db
    def test_schulze_results_adapter_creation(self, test_votes1):
        """Check if schulze results adapter is created."""

        poll_test: PollModel = test_votes1['case1']

        schulze_res: SchulzeResultsAdapter = SchulzeResultsAdapter(poll_test)
        schulze_res.calculate()
        
        assert_that(schulze_res.poll).is_equal_to(poll_test)
        assert_that(schulze_res.schulze_votes).is_not_none()
        assert_that(schulze_res.schulze_results).is_not_none()
        assert_that(schulze_res.schulze_str_options).is_not_none()
        assert_that(schulze_res.all_schulze_rankings).is_not_none()
