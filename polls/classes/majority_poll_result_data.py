from polls.models.majority_judgment_model import MajorityJudgmentModel
from polls.models.poll_option_model import PollOptionModel

from dataclasses import dataclass
import math


@dataclass
class MajorityPollResultData(object):
    """Small class used to store the data related to
    the results of a majority poll"""

    option: PollOptionModel
    """The poll_option the data is related to"""

    good_votes: int
    """The number of good votes performed to this option"""

    median: int
    """The majority grade of the option/poll, called as a median
    of the value of the votes"""

    bad_votes: int
    """The number of bad votes performed to this option"""

    positive_grade: bool
    """The majority grade sign is '+' if good votes are more than
    bad votes"""

    def __init__(self, option: PollOptionModel):

        self.option = option

        # retrieve votes (ordered by rating)
        option_votes = MajorityJudgmentModel.objects \
            .filter(poll_option=option.id) \
            .order_by('rating')

        # calculate median (or worse of two)
        self.median = option_votes[math.floor((option_votes.count()-1)/2)].rating

        # retrieve number of (strictly) greater and smaller votes
        self.good_votes: int = option_votes.filter(rating__gt=self.median).count()
        self.bad_votes: int = option_votes.filter(rating__lt=self.median).count()

        # set sign: 
        # if good > bad         --> +
        # else if good <= bad   --> -
        self.positive_grade = (self.good_votes > self.bad_votes)

    def get_qualitative_median(self) -> str:
        """Get median value as a qualitative judjment"""
        return self.get_qualitative(self.median)
    
    def get_qualitative(self, rating) -> str:
        range = ['Pessimo', 'Insufficiente', 'Sufficiente', 'Buono', 'Ottimo']
        return range[rating-1]

    def get_sign(self) -> str:
        """Get sign (as symbol)"""
        return "+" if self.positive_grade else "-"

    def get_judjment_percentages(self) -> list[dict]: 
        """Get percentage of judjments of each value"""

        all_votes = MajorityJudgmentModel.objects \
            .filter(poll_option=self.option)

        all_votes_n = float(all_votes.count())

        colors = ['#E41A1C', '#FE8E3C', '#FFFFCD', '#7FCEBC', '#253495']
        textcolors = ['white', 'white', 'black', 'black', 'white']

        res: list[dict] = []
        for i in range(1,6):
            value = float(all_votes.filter(rating=i).count())/all_votes_n

            res.append({
                'value': value, 
                'percentage': int(value*100), 
                'style': f"background-color:{colors[i-1]}; color: {textcolors[i-1]}; ", 
                'label': self.get_qualitative(i), 
            })

        return res
        

    def __eq__(self, other): 

        if not isinstance(other, MajorityPollResultData):
            return False

        return self == other
    
    def __gt__(self, other):
        """
        Check if my rating is better than other
        (so if I am semantically ">" than the other one)
        """

        if not isinstance(other, MajorityPollResultData):
            return False
        
        # if median is greater --> x win
        if self.median > other.median:
            return True
        elif self.median < other.median:
            return False

        # positive grade should win against  
        # negative grade
        if self.positive_grade and not other.positive_grade:
            return True
        elif not self.positive_grade and other.positive_grade:
            return False 
        
        # if both are positive, it wins who has greater number of 
        # strictly better votes
        if self.positive_grade and other.positive_grade:
            return self.good_votes > other.good_votes
        elif (not self.positive_grade) and (not other.positive_grade):
            return self.bad_votes < other.bad_votes

        # if both have exactly same votes, I make win 
        # the one with "value" that came before
        return self.option.value > other.option.value