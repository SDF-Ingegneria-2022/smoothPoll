from typing import List
import pytest
from assertpy import assert_that
from apps.polls_management.classes.majority_poll_result_data import MajorityPollResultData
from apps.polls_management.exceptions.majority_number_of_ratings_not_valid import MajorityNumberOfRatingsNotValid
from apps.polls_management.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from polls.models.majority_judgment_model import MajorityJudgmentModel
from polls.models.majority_vote_model import MajorityVoteModel
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.services.majority_vote_service import MajorityVoteService


@pytest.fixture()
def test_polls(request):

    dummy_poll = PollModel(name="Dummy", question="Dummy question?")
    dummy_poll.save()

    option1 = PollOptionModel(value="Valore 1", poll_fk=dummy_poll)
    option1.save()

    option2 = PollOptionModel(value="Valore 2", poll_fk=dummy_poll)
    option2.save()

    option3 = PollOptionModel(value="Valore 3", poll_fk=dummy_poll)
    option3.save()

    control_poll = PollModel(name="Dummy2", question="Dummy question2?")
    control_poll.save()

    option4 = PollOptionModel(value="Valore 1", poll_fk=control_poll)
    option4.save()

    option5 = PollOptionModel(value="Valore 2", poll_fk=control_poll)
    option5.save()

    option6 = PollOptionModel(value="Valore 3", poll_fk=control_poll)
    option6.save()

    option7 = PollOptionModel(value="Valore 4", poll_fk=control_poll)
    option7.save()

    return {'voted_poll': dummy_poll, 'control_poll': control_poll}

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
    def test_majority_vote_perform_works_correctly(self, test_polls):
        """Various test to assert that the majority vote creates the vote correctly"""

        poll: PollModel = test_polls['voted_poll']
        
        votes: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
                            {'poll_choice_id': poll.options()[2].id, 'rating': 3 }]

        performed_vote: MajorityVoteModel = MajorityVoteService.perform_vote(votes, poll_id=poll.id)

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

        assert_that(MajorityVoteService.perform_vote) \
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

        assert_that(MajorityVoteService.perform_vote) \
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

        assert_that(MajorityVoteService.perform_vote) \
            .raises(MajorityNumberOfRatingsNotValid) \
            .when_called_with(votes, poll_id=poll.id)

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

        performed_vote: MajorityVoteModel = MajorityVoteService.perform_vote(votes, poll_id=poll.id)

        MajorityVoteService.calculate_result(poll_id=poll.id)

    @pytest.mark.django_db
    def test_majority_vote_result_notexist_poll(self, test_polls):
        """
        Test that you cannot calculate the results of a majority pool which doesn't exist
        """

        voted_poll: PollModel = test_polls['voted_poll']
        id = voted_poll.id
        voted_poll.delete()

        assert_that(MajorityVoteService.calculate_result) \
            .raises(PollDoesNotExistException) \
            .when_called_with(poll_id=id)

    @pytest.mark.django_db
    def test_majority_vote_calculate_result_check_correct1(self, test_polls):
        """
        Test where the calculate_result is called and chech if the result is correct
        """
        poll: PollModel = test_polls['voted_poll']

        MajorityVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 5 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 2 }], poll_id=poll.id)

        MajorityVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 3 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 5 }], poll_id=poll.id)

        MajorityVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 2 }], poll_id=poll.id)

        x: List[MajorityPollResultData] = MajorityVoteService.calculate_result(poll_id=poll.id)
        
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
                assert_that(option.positive_grade).is_true

    # @pytest.mark.django_db
    # def test_majority_vote_calculate_result_check_correct2(self, test_polls):
    #     """
    #     Test where the calculate_result function is called and chech if the result is correct
    #     """
    #     poll: PollModel = test_polls['voted_poll']

    #     MajorityVoteService.perform_vote(
    #         [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
    #         {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
    #         {'poll_choice_id': poll.options()[2].id, 'rating': 2 }], poll_id=poll.id)

    #     MajorityVoteService.perform_vote(
    #         [{'poll_choice_id': poll.options()[0].id, 'rating': 5 },
    #         {'poll_choice_id': poll.options()[1].id, 'rating': 3 },
    #         {'poll_choice_id': poll.options()[2].id, 'rating': 4 }], poll_id=poll.id)

    #     MajorityVoteService.perform_vote(
    #         [{'poll_choice_id': poll.options()[0].id, 'rating': 3 },
    #         {'poll_choice_id': poll.options()[1].id, 'rating': 3 },
    #         {'poll_choice_id': poll.options()[2].id, 'rating': 4 }], poll_id=poll.id)

    #     x: List[MajorityPollResultData] = MajorityVoteService.calculate_result(poll_id=poll.id)

    #     # verify option values
    #     for option in x:

    #         if option.poll_option_data == poll.options()[0]:
    #             # votes on option 0: [2, 3, 5 ]
    #             assert_that(option.median).is_equal_to()
    #             assert_that(option.good_votes).is_equal_to()
    #             assert_that(option.bad_votes).is_equal_to()
    #             assert_that(option.positive_grade)
    #             assert_that(option.negative_grade)

    #         elif option.poll_option_data == poll.options()[1]:
    #             # votes on option 1:  [2, 3, 3 ]
    #             assert_that(option.median).is_equal_to()
    #             assert_that(option.good_votes).is_equal_to()
    #             assert_that(option.bad_votes).is_equal_to()
    #             assert_that(option.positive_grade)
    #             assert_that(option.negative_grade)
    #         else:
    #             # votes on option 2: [2, 4, 4]
    #             assert_that(option.median).is_equal_to()
    #             assert_that(option.good_votes).is_equal_to()
    #             assert_that(option.bad_votes).is_equal_to()
    #             assert_that(option.positive_grade)
    #             assert_that(option.negative_grade)

    @pytest.mark.django_db
    def test_majority_vote_calculate_result_check_correct3(self, test_polls):
        """
        Test where the calculate_result function is called and chech if the result is correct
        """
        poll: PollModel = test_polls['voted_poll']

        MajorityVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
             {'poll_choice_id': poll.options()[1].id, 'rating': 5 },
             {'poll_choice_id': poll.options()[2].id, 'rating': 5 }], poll_id=poll.id)

        MajorityVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
             {'poll_choice_id': poll.options()[1].id, 'rating': 5 },
             {'poll_choice_id': poll.options()[2].id, 'rating': 5 }], poll_id=poll.id)

        MajorityVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
             {'poll_choice_id': poll.options()[1].id, 'rating': 4 },
             {'poll_choice_id': poll.options()[2].id, 'rating': 5 }], poll_id=poll.id)

        MajorityVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
             {'poll_choice_id': poll.options()[1].id, 'rating': 4 },
             {'poll_choice_id': poll.options()[2].id, 'rating': 5 }], poll_id=poll.id)

        x: List[MajorityPollResultData] = MajorityVoteService.calculate_result(poll_id=poll.id)

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


    # @pytest.mark.django_db
    # def test_majority_vote_calculate_result_check_correct4(self, test_polls):
    #     """
    #     Test where the calculate_result function is called and chech if the result is correct
    #     """
    #     poll: PollModel = test_polls['voted_poll']

    #     votes: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
    #                         {'poll_choice_id': poll.options()[1].id, 'rating': 5 },
    #                         {'poll_choice_id': poll.options()[2].id, 'rating': 5 }]

    #     performed_vote: MajorityVoteModel = MajorityVoteService.perform_vote(votes, poll_id=poll.id)

    #     votes1: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
    #                         {'poll_choice_id': poll.options()[1].id, 'rating': 5 },
    #                         {'poll_choice_id': poll.options()[2].id, 'rating': 5 }]

    #     performed_vote: MajorityVoteModel = MajorityVoteService.perform_vote(votes1, poll_id=poll.id)

    #     votes2: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
    #                         {'poll_choice_id': poll.options()[1].id, 'rating': 4 },
    #                         {'poll_choice_id': poll.options()[2].id, 'rating': 5 }]

    #     performed_vote: MajorityVoteModel = MajorityVoteService.perform_vote(votes2, poll_id=poll.id)

    #     votes3: List[dict] = [{'poll_choice_id': poll.options()[0].id, 'rating': 3 },
    #                         {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
    #                         {'poll_choice_id': poll.options()[2].id, 'rating': 5 }]

    #     performed_vote: MajorityVoteModel = MajorityVoteService.perform_vote(votes3, poll_id=poll.id)

    #     x: List[MajorityPollResultData] = MajorityVoteService.calculate_result(poll_id=poll.id)

    #     assert_that(x[0].good_votes).is_equal_to(4)
    #     assert_that(x[0].median).is_equal_to(3)
    #     assert_that(x[0].bad_votes).is_equal_to(0)

    #     assert_that(x[1].good_votes).is_equal_to(3)
    #     assert_that(x[1].median).is_equal_to(3)
    #     assert_that(x[1].bad_votes).is_equal_to(1)

    #     assert_that(x[2].good_votes).is_equal_to(0)
    #     assert_that(x[2].median).is_equal_to(3)
    #     assert_that(x[2].bad_votes).is_equal_to(3)

    @pytest.mark.django_db
    def test_majority_vote_calculate_result_check_correct5(self, test_polls):
        """
        Test where the calculate_result function is called and chech if the result is correct
        """
        poll: PollModel = test_polls['control_poll']

        MajorityVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 4 },
            {'poll_choice_id': poll.options()[3].id, 'rating': 4 }], poll_id=poll.id)

        MajorityVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 5 },
            {'poll_choice_id': poll.options()[3].id, 'rating': 2 }], poll_id=poll.id)

        MajorityVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 1 },
            {'poll_choice_id': poll.options()[3].id, 'rating': 2 }], poll_id=poll.id)

        MajorityVoteService.perform_vote(
            [{'poll_choice_id': poll.options()[0].id, 'rating': 3 },
            {'poll_choice_id': poll.options()[1].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[2].id, 'rating': 2 },
            {'poll_choice_id': poll.options()[3].id, 'rating': 2 }], poll_id=poll.id)

        x: List[MajorityPollResultData] = MajorityVoteService.calculate_result(poll_id=poll.id)

                # verify options order
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