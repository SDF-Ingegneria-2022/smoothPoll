
import pytest

from test.utils.create_polls_utils import create_single_option_polls

class TestShortIdGenerator:
    
    @pytest.fixture()
    def create_polls(request,django_user_model):
        """Fixture for creating polls."""
        create_single_option_polls(django_user_model)
    
    
    def test_id_generation(self, create_polls):
        """Test id generation."""
        
        pass