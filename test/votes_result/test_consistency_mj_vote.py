from typing import List
from assertpy import assert_that
from apps.votes_results.classes.check_consistency_mj_vote import CheckConsistencyMjVote


class TestCheckConsitencyMjVote:
    def test_check_valid_concistency(self):
        single_option_vote_key: str = '1'
        mj_votes: List[dict] = self._create_mj_votes([3, 1, 1])
        sut: bool = CheckConsistencyMjVote.check(single_option_vote_key, mj_votes)
        
        assert_that(sut).is_true()
        
    def test_check_not_valid_concistency(self):
        single_option_vote_key: str = "1"
        mj_votes: List[dict] = self._create_mj_votes([1, 3, 4])
        sut: bool = CheckConsistencyMjVote.check(single_option_vote_key, mj_votes)
        
        assert_that(sut).is_false()
    
    def test_check_valid_concistency_with_same_rating(self):
        single_option_vote_key: str = "1"
        mj_votes: List[dict] = self._create_mj_votes([3, 3, 3])
        sut: bool = CheckConsistencyMjVote.check(single_option_vote_key, mj_votes)
        
        assert_that(sut).is_true()
        
        
        
    def _create_mj_votes(self, list_of_ratings: List[int]) -> List[dict]:
        mj_votes: list = []
        for index, item in enumerate(list_of_ratings):
            mj_votes.append({'poll_choice_id': index + 1, 'rating': item})
            
        return mj_votes