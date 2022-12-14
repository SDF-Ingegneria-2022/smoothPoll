from polls.services.poll_create_service import PollCreateService


from typing import Dict, List
import pytest

class TestPollService:
    """Test suite that covers all methods in the PollService class"""

    name1: str = "Sondaggio cibo"
    question1: str = "Qual è il tuo cibo preferito?"
    options1: List[str] = ["Pizza", "Pasta", "Carne", "Pesce", "Altro", ]

    name2: str = "Sondaggio cibo pt. 2"
    question2: str = "Ti piace il pesce crudo?"
    options2: List[str] = ["Si", "No",]

    unvalid_options1: List[str] = ["Si :)", ]
    unvalid_options2: List[str] = [str(i) for i in range(1,12)] 
    """numbers from 1 to 11 as str 
    (too many for current options constrains)"""

    ## Fixtures
    # @pytest.fixture
    # def create_20_polls(self):
    #     """Creates 20 polls"""
    #     for poll_index in range(20):
    #         new_poll: PollModel = PollModel(name=f"Poll {poll_index}", question=f"Question {poll_index} ?")
    #         new_poll.save()
    #         for option_index in range(2):
    #             PollOptionModel(value=f"Option {option_index}", poll_fk_id=new_poll.id).save()

    @pytest.mark.django_db
    def test_create_poll_runs(self):
        """Simple test to check if creation does not crash (it runs)"""
    
        PollCreateService.create_new_poll(self.name1, self.options1)
        

    @pytest.mark.django_db
    def test_create_poll_ok1(self):
        """Check if object is created, aside with all options"""
    
        poll = PollCreateService.create_new_poll(self.name1, self.options1)
