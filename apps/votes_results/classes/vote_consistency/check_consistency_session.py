from typing import List
from django.http import HttpRequest

from apps.polls_management.models.poll_model import PollModel
from apps.votes_results.classes.vote_consistency.check_consistency_mj_vote import CheckConsistencyMjVote


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
        
        if (
            poll.poll_type == PollModel.PollType.SINGLE_OPTION and \
            self._request.session.get(session_single_option_vote_id) and \
    
            self._request.session.get(session_consistency_check) is None and
            not CheckConsistencyMjVote.check(self._request.session.get(session_single_option_vote_id), mj_ratings)):
                
                # Options selected by the user in order to perform the unconsistent vote if the user wants to perform
                options_selected: dict = {
                                            'id': []
                                        }
                for key, value in self._request.POST.items():
                    if not key == 'csrfmiddlewaretoken':
                        options_selected['id'].append(int(key))
                        options_selected[int(key)] =  int(value)
                
                self._request.session[session_consistency_check] = {
                                                                    'check': True,
                                                                    'options_selected': options_selected
                                                                    }
                
                return True
        else:
            return False
    
    def consistency_check_is_avalable_in_session(self, session_consistency_check: str) -> bool:
        """Checks if the consistency check is available in session.
        Args:
            session_consistency_check (str): The session consistency check parameter.
        Returns:
            bool: True if the consistency check is available in session, False otherwise.
        """
        return self._request.session.get(session_consistency_check) is not None
    
    def clear_session(self, consistency_session_params: List[str]) -> None:
        """Clears the consistency session parameters. In safe mode.
        Args:
            consistency_session_params (List[str]): The consistency session parameters.
        """
        
        for param in consistency_session_params:
            if self._request.session.get(param) is not None:
                del self._request.session[param]
                
        