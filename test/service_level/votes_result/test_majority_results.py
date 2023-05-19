from typing import List
import pytest
from assertpy import assert_that
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException

from apps.polls_management.models.majority_vote_model import MajorityVoteModel

from apps.polls_management.models.poll_model import PollModel
from apps.votes_results.classes.majority_poll_result_data import MajorityPollResultData
from apps.votes_results.services.majority_judgment_vote_service import MajorityJudjmentVoteService
from test.service_level.utils.has_test_polls import HasTestPolls


class TestMajorityResults(HasTestPolls):

    # Section related to tests of method calculate_result

    @pytest.mark.django_db
    def test_majority_vote_calculate_result_call(self, test_polls):
        """
        Test where the calculate_result function is only called
        """
        poll: PollModel = test_polls['voted_poll']

        votes: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[2].id, 'rating': 3 }]

        performed_vote: MajorityVoteModel = MajorityJudjmentVoteService.perform_vote(votes, poll_id=poll.id)

        MajorityJudjmentVoteService.calculate_result(poll_id=poll.id)

    @pytest.mark.django_db
    def test_majority_vote_result_notexist_poll(self, test_polls):
        """
        Test that you cannot calculate the results of a majority pool which doesn't exist
        """

        voted_poll: PollModel = test_polls['voted_poll']
        id = voted_poll.id
        voted_poll.delete()

        assert_that(MajorityJudjmentVoteService.calculate_result) \
            .raises(PollDoesNotExistException) \
            .when_called_with(poll_id=id)

    @pytest.mark.django_db
    def test_majority_vote_calculate_result_check_correct1(self, test_polls):
        """
        Test where the calculate_result is called and chech if the result is correct
        """
        poll: PollModel = test_polls['voted_poll']

        MajorityJudjmentVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 5 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 2 }], poll_id=poll.id)

        MajorityJudjmentVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 3 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 5 }], poll_id=poll.id)

        MajorityJudjmentVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 2 }], poll_id=poll.id)

        x: List[MajorityPollResultData] = MajorityJudjmentVoteService.calculate_result(
            poll_id=poll.id).get_sorted_options_no_parity()
        
        # verify options order
        assert_that(x[0].option).is_equal_to(poll.options()[0])
        assert_that(x[1].option).is_equal_to(poll.options()[2])
        assert_that(x[2].option).is_equal_to(poll.options()[1])

        # verify option values
        for option in x:

            if option.option == poll.options()[0]:
                # votes on option 0: [1, 3, 5 ]
                assert_that(option.median).is_equal_to(3)
                assert_that(option.good_votes).is_equal_to(1)
                assert_that(option.bad_votes).is_equal_to(1)
                assert_that(option.positive_grade).is_false()

            elif option.option == poll.options()[1]:
                # votes on option 1: [1, 2, 2] 
                assert_that(option.median).is_equal_to(2)
                assert_that(option.good_votes).is_equal_to(0)
                assert_that(option.bad_votes).is_equal_to(1)
                assert_that(option.positive_grade).is_false()
            else:
                # votes on option 2: [2, 2, 5]
                assert_that(option.median).is_equal_to(2)
                assert_that(option.good_votes).is_equal_to(1)
                assert_that(option.bad_votes).is_equal_to(0)
                assert_that(option.positive_grade).is_true()

    @pytest.mark.django_db
    def test_majority_vote_calculate_result_check_correct3(self, test_polls):
        """
        Test where the calculate_result function is called and chech if the result is correct
        """
        poll: PollModel = test_polls['voted_poll']

        MajorityJudjmentVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
             {'poll_choice_id': poll.options()[1].id, 'rating': 5 },
             {'poll_choice_id': poll.options()[2].id, 'rating': 5 }], poll_id=poll.id)

        MajorityJudjmentVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
             {'poll_choice_id': poll.options()[1].id, 'rating': 5 },
             {'poll_choice_id': poll.options()[2].id, 'rating': 5 }], poll_id=poll.id)

        MajorityJudjmentVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
             {'poll_choice_id': poll.options()[1].id, 'rating': 4 },
             {'poll_choice_id': poll.options()[2].id, 'rating': 5 }], poll_id=poll.id)

        MajorityJudjmentVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
             {'poll_choice_id': poll.options()[1].id, 'rating': 4 },
             {'poll_choice_id': poll.options()[2].id, 'rating': 5 }], poll_id=poll.id)

        x: List[MajorityPollResultData] = MajorityJudjmentVoteService.calculate_result(
            poll_id=poll.id).get_sorted_options_no_parity()
        
        # verify options order
        assert_that(x[0].option).is_equal_to(poll.options()[2])
        assert_that(x[1].option).is_equal_to(poll.options()[1])
        assert_that(x[2].option).is_equal_to(poll.options()[0])

        # verify option values
        for option in x:
            
            if option.option == poll.options()[0]:
                # votes on option 0: [1, 1, 1, 2]
                assert_that(option.median).is_equal_to(1)
                assert_that(option.good_votes).is_equal_to(1)
                assert_that(option.bad_votes).is_equal_to(0)
                assert_that(option.positive_grade).is_true()

            elif option.option == poll.options()[1]:
                # votes on option 1:  [4, 4, 5, 5]
                assert_that(option.median).is_equal_to(4)
                assert_that(option.good_votes).is_equal_to(2)
                assert_that(option.bad_votes).is_equal_to(0)
                assert_that(option.positive_grade).is_true()
            else:
                # votes on option 2: [5, 5, 5, 5]
                assert_that(option.median).is_equal_to(5)
                assert_that(option.good_votes).is_equal_to(0)
                assert_that(option.bad_votes).is_equal_to(0)
                assert_that(option.positive_grade).is_false()

    @pytest.mark.django_db
    def test_majority_vote_calculate_result_check_correct5(self, test_polls):
        """
        Test where the calculate_result function is called and chech if the result is correct
        """
        poll: PollModel = test_polls['control_poll']

        MajorityJudjmentVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 4 },
            {'poll_choice_id': poll.options()[3].id, 'rating': 4 }], poll_id=poll.id)

        MajorityJudjmentVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 5 },
            {'poll_choice_id': poll.options()[3].id, 'rating': 2 }], poll_id=poll.id)

        MajorityJudjmentVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[3].id, 'rating': 2 }], poll_id=poll.id)

        MajorityJudjmentVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 3 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[3].id, 'rating': 2 }], poll_id=poll.id)

        x: List[MajorityPollResultData] = MajorityJudjmentVoteService.calculate_result(
            poll_id=poll.id).get_sorted_options_no_parity()

        # verify options order 2, 3, 1, 0
        assert_that(x[0].option).is_equal_to(poll.options()[2])
        assert_that(x[1].option).is_equal_to(poll.options()[3])
        assert_that(x[2].option).is_equal_to(poll.options()[1])
        assert_that(x[3].option).is_equal_to(poll.options()[0])

        # verify option values
        for option in x:
            
            if option.option == poll.options()[0]:
                # votes on option 0: [1, 1, 2, 3]
                assert_that(option.median).is_equal_to(1)
                assert_that(option.good_votes).is_equal_to(2)
                assert_that(option.bad_votes).is_equal_to(0)
                assert_that(option.positive_grade).is_true()

            elif option.option == poll.options()[1]:
                # votes on option 1:  [1, 2, 2, 2]
                assert_that(option.median).is_equal_to(2)
                assert_that(option.good_votes).is_equal_to(0)
                assert_that(option.bad_votes).is_equal_to(1)
                assert_that(option.positive_grade).is_false()

            elif option.option == poll.options()[2]:
                # votes on option 1:  [1, 2, 4, 5]
                assert_that(option.median).is_equal_to(2)
                assert_that(option.good_votes).is_equal_to(2)
                assert_that(option.bad_votes).is_equal_to(1)
                assert_that(option.positive_grade).is_true()

            else:
                # votes on option 2: [2, 2, 2, 4]
                assert_that(option.median).is_equal_to(2)
                assert_that(option.good_votes).is_equal_to(1)
                assert_that(option.bad_votes).is_equal_to(0)
                assert_that(option.positive_grade).is_true()


    # -------------------- tests for majority revision algorithm --------------------

    def __quick_submit_vote(self, poll: PollModel, ratings: List[int]):

        MajorityJudjmentVoteService.perform_vote(
            [
                {
                    'poll_choice_id': poll.options()[i].id, 
                    'rating': ratings[i], 
                }
                for i in range(len(ratings))
            ], poll_id=poll.id)

    @pytest.mark.django_db
    def test_majority_vote_calculate_result_check_correct_special_case1(self, test_polls):
        """
        Test where the calculate_result function is called and chech if the result is correct
        """
        poll: PollModel = test_polls['poll_case_1']

        # option[0] = A <-- 1-22-3-4-55
        # option[1] = B <-- 111-444-5
        # option[2] = C <-- 11-2-33-55
        # option[3] = D <-- 1-333-555
        # number of votes = 7
        # expected result: B > D > A > C

        self.__quick_submit_vote(poll, [1, 1, 1, 1]) 
        self.__quick_submit_vote(poll, [2, 1, 1, 3])
        self.__quick_submit_vote(poll, [2, 1, 2, 3])
        self.__quick_submit_vote(poll, [3, 4, 3, 3])
        self.__quick_submit_vote(poll, [4, 4, 3, 5])
        self.__quick_submit_vote(poll, [5, 4, 5, 5])
        self.__quick_submit_vote(poll, [5, 5, 5, 5])
       
        x: List[List[MajorityPollResultData]] = \
            MajorityJudjmentVoteService.calculate_result(
            poll_id=poll.id).get_sorted_options()
        

        assert_that(x[0][0].option).is_equal_to(poll.options()[1])
        assert_that(x[1][0].option).is_equal_to(poll.options()[3])
        assert_that(x[2][0].option).is_equal_to(poll.options()[0])
        assert_that(x[3][0].option).is_equal_to(poll.options()[2])


    @pytest.mark.django_db
    def test_majority_vote_calculate_result_check_correct_special_case2(self, test_polls):

        poll: PollModel = test_polls['poll_case_23']

        # option[0] = A <-- 444-555
        # option[1] = B <-- 222-444
        # option[2] = C <-- 11-3-555
        # option[3] = D <-- 11-33-55
        # option[4] = E <-- 11-2-555
        # number of votes = 6
        # expected result: A > C > D > E > B 

        self.__quick_submit_vote(poll, [4, 2, 1, 1, 1])
        self.__quick_submit_vote(poll, [4, 2, 1, 1, 1])
        self.__quick_submit_vote(poll, [4, 2, 3, 3, 2])
        self.__quick_submit_vote(poll, [5, 4, 5, 3, 5])
        self.__quick_submit_vote(poll, [5, 4, 5, 5, 5])
        self.__quick_submit_vote(poll, [5, 4, 5, 5, 5])

        x: List[List[MajorityPollResultData]] = \
            MajorityJudjmentVoteService.calculate_result(
            poll_id=poll.id).get_sorted_options()
        
        assert_that(x[0][0].option).is_equal_to(poll.options()[0])
        assert_that(x[1][0].option).is_equal_to(poll.options()[2])
        assert_that(x[2][0].option).is_equal_to(poll.options()[3])
        assert_that(x[3][0].option).is_equal_to(poll.options()[4])
        assert_that(x[4][0].option).is_equal_to(poll.options()[1])

    # @pytest.mark.django_db
    # def test_majority_vote_calculate_result_check_correct_special_case3(self, test_polls):

    #     poll: PollModel = test_polls['poll_case_23']

    #     # option[0] = A <-- 2-333-5
    #     # option[1] = B <-- 2-333-5
    #     # option[2] = C <-- 1-33-44
    #     # option[3] = D <-- 1-33-44
    #     # option[4] = E <-- 11-333
    #     # number of votes = 5
    #     # expected result: C = D > A = B > E

    #     self.__quick_submit_vote(poll, [2, 2, 1, 1, 1])
    #     self.__quick_submit_vote(poll, [3, 3, 3, 3, 1])
    #     self.__quick_submit_vote(poll, [3, 3, 3, 3, 3])
    #     self.__quick_submit_vote(poll, [3, 3, 4, 4, 3])
    #     self.__quick_submit_vote(poll, [5, 5, 4, 4, 3])

    #     x: List[List[MajorityPollResultData]] = MajorityJudjmentVoteService.calculate_result(
    #         poll_id=poll.id).get_sorted_options()
        
    
    #     assert_that(x[0].option).is_equal_to(poll.options()[2])
    #     assert_that(x[1].option).is_equal_to(poll.options()[3])
    #     assert_that(x[2].option).is_equal_to(poll.options()[0])
    #     assert_that(x[3].option).is_equal_to(poll.options()[1])
    #     assert_that(x[4].option).is_equal_to(poll.options()[4])

