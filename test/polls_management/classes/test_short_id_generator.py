
import pytest
from assertpy import assert_that
from apps.polls_management.classes.poll_form_utils.short_id_util import ShortIdUtil
from apps.polls_management.models.poll_model import PollModel
from test.utils.create_polls_utils import create_single_option_polls

class TestShortIdGenerator:
    
    @pytest.fixture()
    def create_polls(request,django_user_model):
        """Fixture for creating polls."""
        create_single_option_polls(django_user_model)
    
    
    def test_id_generation(self, create_polls):
        """Test id generation."""
        
        sut: str = ShortIdUtil.generate()
        
        assert_that(sut).is_not_none()
        assert_that(sut).is_length(6)
        
    def test_short_id_is_unique(self, create_polls):
        """Test that the short id is unique."""
        
        sut: str = ShortIdUtil.generate()
        
        assert_that(sut).is_not_in(list(PollModel.objects.values_list('short_id', flat=True)))
        
    def test_short_id_is_valid(self, create_polls):
        """Test that the short id is valid."""
        short_id: str = ShortIdUtil.generate()
        
        sut: bool = ShortIdUtil.validate(short_id)
        
        assert_that(sut).is_true()
        
    def test_short_id_is_valid(self, create_polls):
        """Test that the short id is valid."""
        short_id: str = ShortIdUtil.generate() + "a"
        
        sut: bool = ShortIdUtil.validate(short_id)
        
        assert_that(sut).is_false()
        
    
        
    