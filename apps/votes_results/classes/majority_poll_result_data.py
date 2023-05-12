from apps.polls_management.models.majority_judgment_model import MajorityJudgmentModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.votes_results.exceptions.poll_not_yet_voted_exception import PollNotYetVodedException

from django.db.models.query import QuerySet

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

    option_votes: QuerySet
    """All the votes for this option"""

    def __init__(self, option: PollOptionModel):

        self.option = option

        # retrieve votes (ordered by rating)
        self.option_votes = MajorityJudgmentModel.objects \
            .filter(poll_option=option.id) \
            .order_by('rating')

        if self.option_votes.count() < 1:
            raise PollNotYetVodedException()

        # calculate median (or worse of two)
        self.median = self.option_votes[math.floor((self.option_votes.count()-1)/2)].rating

        # retrieve number of (strictly) greater and smaller votes
        self.good_votes: int = self.option_votes.filter(rating__gt=self.median).count()
        self.bad_votes: int = self.option_votes.filter(rating__lt=self.median).count()

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
            if value > 0:
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

        return self.sorting(other, 0)
    
    def majority_values_median(self, values: list[MajorityJudgmentModel]) -> int:
        """Returns new median from list of majority values"""

        old_median = values[math.floor(len(values)/2)]

        if len(values) > 1:
            # here we exclude the single value of the median
            values.remove(old_median)
            new_median = values[math.floor(len(values)/2)].rating
        
            return new_median
        else:
            return old_median

    def median_value(self, iteration=0) -> int:
        """Calculates the median of the current majority values iteration"""

        majority_values: list[MajorityJudgmentModel] = list(self.option_votes)

        if iteration > 0:
            while(iteration > 0):
                new_median = self.majority_values_median(majority_values)
                iteration -= 1
            return new_median
        else:
            return self.median
        
    def sorting(self, obj, i) -> bool:
        """Function that gives sorting rules for Majority Poll Result Data Objects"""
        
        if i == self.option_votes.count():
            return self.option.value < obj.option.value

        # if median is greater --> x win
        if self.median_value(iteration=i) > obj.median_value(iteration=i):
            return True
        elif self.median_value(iteration=i) < obj.median_value(iteration=i):
            return False
        else:
            return self.sorting(obj, i+1)
