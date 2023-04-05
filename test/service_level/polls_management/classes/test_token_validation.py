from typing import List
import pytest
from assertpy import assert_that
from apps.polls_management.classes.poll_token_validation.token_validation import TokenValidation
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens
from test.service_level.utils.create_polls_utils import create_single_option_polls

class TestTokenValidation:

    @pytest.fixture
    def create_user(self, django_user_model):
        username = "user1"
        password = "bar"
        user = django_user_model.objects.create_user(username=username, password=password)
        return user
    
    @pytest.fixture()
    def create_polls(request,django_user_model):
        """Fixture for creating polls."""
        create_single_option_polls(django_user_model)
        
    @pytest.mark.django_db
    def test_token_validation(self, create_polls, create_user):
        """Various tests to check token validity"""
        
        user = create_user
        polls: List[PollModel] = PollModel.objects.all()

        poll_single: PollModel = polls[0]
        poll_majority: PollModel = polls[1]
        poll_mj: PollModel = polls[2]

        poll_single.votable_mj = False
        poll_single.save()

        poll_majority.votable_mj = False
        poll_majority.poll_type = PollModel.PollType.MAJORITY_JUDJMENT
        poll_majority.save()

        # normal test, token usable
        test_token1: PollTokens = PollTokens(token_user=user, poll_fk=poll_single)
        test_token2: PollTokens = PollTokens(token_user=user, poll_fk=poll_majority)
        test_token3: PollTokens = PollTokens(token_user=user, poll_fk=poll_mj)

        assert_that(TokenValidation.validate(poll=poll_single, token=test_token1)).is_true()
        assert_that(TokenValidation.validate(poll=poll_majority, token=test_token2)).is_true()
        assert_that(TokenValidation.validate(poll=poll_mj, token=test_token3)).is_true()

        # bad test, token not valid
        test_token1.single_option_use = True
        test_token1.save()
        test_token2.majority_use = True
        test_token2.save()
        test_token3.single_option_use = True
        test_token3.majority_use = True
        test_token3.save()

        assert_that(TokenValidation.validate(poll=poll_single, token=test_token1)).is_false()
        assert_that(TokenValidation.validate(poll=poll_majority, token=test_token2)).is_false()
        assert_that(TokenValidation.validate(poll=poll_mj, token=test_token3)).is_false()

        # test special case for votable mj
        test_token3.majority_use = False
        test_token3.save()

        assert_that(TokenValidation.validate(poll=poll_mj, token=test_token3)).is_false()
        assert_that(TokenValidation.validate_mj_special_case(poll=poll_mj, token=test_token3)).is_true()

        # mixed tests, token type checks for not same type of poll
        test_token1.single_option_use = False
        test_token1.save()

        assert_that(TokenValidation.validate(poll=poll_single, token=test_token1)).is_true()

        test_token2.majority_use = False
        test_token2.save()

        assert_that(TokenValidation.validate(poll=poll_majority, token=test_token2)).is_true()

        # unusual/impossible case for validate_mj_special_case
        test_token3.single_option_use = False
        test_token3.majority_use = True
        test_token3.save()

        assert_that(TokenValidation.validate_mj_special_case(poll=poll_mj, token=test_token3)).is_false()


