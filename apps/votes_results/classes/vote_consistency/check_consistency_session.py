from typing import List
from django.http import HttpRequest

from apps.polls_management.models.poll_model import PollModel
from apps.votes_results.classes.vote_consistency.check_consistency_mj_vote import CheckConsistencyMjVote
from apps.votes_results.classes.vote_consistency.check_consistency_shulze import CheckConsistencyShulze


class CheckConsistencySession:
    def __init__(self, request: HttpRequest) -> None:
        self._request: HttpRequest = request
        

    
    def check_consistency(self, poll: PollModel, 
                                mj_ratings: List[dict], 
                                session_single_option_vote_id: str, 
                                session_consistency_check: str) -> bool:
        """Checks if the single option vote is consistent with the mj choises. If the vote is not consistent returns 
        True, otherwise False. In case of vote is not consiste, it updates the session parameter in order to notify 
        the user about the inconsistency.
        
        Returns:
            bool: True if the vote is not consisnte, False otherwise.
        """
        
        if (self._checks_for_single_option(poll, session_single_option_vote_id, session_consistency_check, mj_ratings) or \
            self._checks_for_schulze(poll, session_single_option_vote_id, session_consistency_check, mj_ratings)):
                
                # Options selected by the user in order to perform the unconsistent vote if the user wants to perform it.
                self._request.session[session_consistency_check] = {
                                                                    'check': True,
                                                                    'options_selected': self._get_mj_options_selected(self._request.POST.items())
                                                                    }
                
                return True # Vote non consistent
        else:
            return False
    
    def clear_session(self, consistency_session_params: List[str]) -> None:
        """Clears the consistency session parameters. In safe mode.
        Args:
            consistency_session_params (List[str]): The consistency session parameters.
        """
        
        for param in consistency_session_params:
            if self._request.session.get(param) is not None:
                del self._request.session[param]
                
                
    def _get_mj_options_selected(self, options_selected_from_request: List ) -> dict:
        options_selected: dict = {
                                            'id': []
                                        }
        
        for key, value in options_selected_from_request:
                    if not key == 'csrfmiddlewaretoken':
                        options_selected['id'].append(int(key))
                        options_selected[int(key)] =  int(value)
                        
        return options_selected
    
    
    def _checks_for_single_option(self, poll, vote_id, session_consistency_check, mj_ratings) -> bool:
        return  poll.poll_type == PollModel.PollType.SCHULZE and \
                self._request.session.get(vote_id) and \
                self._request.session.get(session_consistency_check) is None and \
                not CheckConsistencyMjVote.check(self._request.session.get(vote_id), mj_ratings)
                
    def _checks_for_schulze(self, poll, vote_id, session_consistency_check, mj_ratings) -> bool:
        return  poll.poll_type == PollModel.PollType.SCHULZE and \
                self._request.session.get(vote_id) and \
                self._request.session.get(session_consistency_check) is None and \
                not CheckConsistencyShulze.check(self._request.session.get(vote_id), mj_ratings)