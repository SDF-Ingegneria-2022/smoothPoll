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

        return self.sorting(other, i=0)

        # if not isinstance(other, MajorityPollResultData):
        #     return False
        
        # # if median is greater --> x win
        # if self.median > other.median:
        #     return True
        # elif self.median < other.median:
        #     return False

        # # positive grade should win against  
        # # negative grade
        # if self.positive_grade and not other.positive_grade:
        #     return True
        # elif not self.positive_grade and other.positive_grade:
        #     return False 
        
        # # if both are positive, it wins who has greater number of 
        # # strictly better votes
        # if self.positive_grade and other.positive_grade:
        #     return self.good_votes > other.good_votes
        # elif (not self.positive_grade) and (not other.positive_grade):
        #     return self.bad_votes < other.bad_votes

        # # if both have exactly same votes, I make win 
        # # the one with "value" that came before
        # return self.option.value > other.option.value
    
    def majority_values_median(self, values: QuerySet):
        """Returns new median from list of majority values"""

        old_median = values[math.floor((values.count()-1)/2)].rating

        if values.count() > 1:
            # here we exclude the single value of the median
            values.exclude(rating=old_median)
            new_median = values[math.floor((values.count()-1)/2)].rating
        
            return new_median
        else:
            return old_median

    def median_value(self, iteration=0):
        """Calculates the median of the current majority values iteration"""

        majority_values: QuerySet = self.option_votes

        if iteration > 0:
            while(iteration > 0):
                new_median = self.majority_values_median(majority_values)
                iteration -= 1
            return new_median
        else:
            return self.median
        
    def good_votes_value(self, it_g=0):
        """Calculates the number of good votes for the current majority value iteration"""

        majority_values: QuerySet = self.option_votes

        if it_g > 0:
            while(it_g > 0):
                new_median = self.majority_values_median(majority_values)
                it_g -= 1
            new_good_votes: int = majority_values.filter(rating__gt=new_median).count()
            return new_good_votes
        else:
            return self.good_votes
        
    def bad_votes_value(self, it_b=0):
        """Calculates the number of bad votes for the current majority value iteration"""

        majority_values: QuerySet = self.option_votes

        if it_b > 0:
            while(it_b > 0):
                new_median = self.majority_values_median(majority_values)
                it_b -= 1
            new_bad_votes: int = majority_values.filter(rating__lt=new_median).count()
            return new_bad_votes
        else:
            return self.bad_votes
        
    def positive_grade_value(self, iteration=0):
        """Calculates the positive grade for the current majority value iteration"""

        if iteration > 0:
            new_positive_grade = (self.good_votes_value(it_g=iteration) > self.bad_votes_value(it_b=iteration))
            return new_positive_grade
        else:
            return self.positive_grade

    def sorting(self, obj, i):
        """Function that gives sorting rules for Majority Data Objects"""

        if not isinstance(obj, MajorityPollResultData):
            return False
        
        if i == self.option_votes.count()-1:
            return self.option.value > obj.option.value

        # if median is greater --> x win
        if self.median_value(iteration=i) > obj.median_value(iteration=i):
            return True
        elif self.median_value(iteration=i) < obj.median_value(iteration=i):
            return False

        # positive grade should win against  
        # negative grade
        if self.positive_grade_value(iteration=i) and not obj.positive_grade_value(iteration=i):
            return True
        elif not self.positive_grade_value(iteration=i) and obj.positive_grade_value(iteration=i):
            return False 
        
        # if both are positive, it wins who has greater number of 
        # strictly better votes
        if self.positive_grade_value(iteration=i) and obj.positive_grade_value(iteration=i):
            # special case where (p, grade, q) => grade1==grade2 (with same sign) and p1==p2 or q1==q2
            # here we use the iterations to get the majority values
            if self.good_votes_value(it_g=i) == obj.good_votes_value(it_g=i) and \
                not (self.bad_votes_value(it_b=i) == obj.bad_votes_value(it_b=i)):

                return self.sorting(obj, i+1)
            else:
                return self.good_votes_value(it_g=i) > obj.good_votes_value(it_g=i)
        elif (not self.positive_grade_value(iteration=i)) and (not obj.positive_grade_value(iteration=i)):
            # special case where (p, grade, q) => grade1==grade2 (with same sign) and p1==p2 or q1==q2
            # here we use the iterations to get the majority values
            if self.bad_votes_value(it_b=i) == obj.bad_votes_value(it_b=i) and \
                not (self.good_votes_value(it_g=i) == obj.good_votes_value(it_g=i)):

                return self.sorting(obj, i+1)
            else:
                return self.bad_votes_value(it_b=i) < obj.bad_votes_value(it_b=i)

        # special case where (p, grade, q) => grade1==grade2 (with same sign) and p1==p2 or q1==q2
        # here we use the iterations to get the majority values
        # if ((self.good_votes_value(it_g=i) == obj.good_votes_value(it_g=i)) or \
        #     (self.bad_votes_value(it_b=i) == obj.bad_votes_value(it_b=i))):
        #     return self.sorting(obj, i+1)

        # if both have exactly same votes, I make win 
        # the one with "value" that came before
        return self.option.value > obj.option.value