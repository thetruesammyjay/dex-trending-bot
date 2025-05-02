import pytest
from unittest.mock import patch, MagicMock
from src.twitter_search import (
    find_relevant_twitter_accounts,
    is_eligible_account
)

@pytest.fixture
def mock_twitter_response():
    mock = MagicMock()
    mock.includes = {'users': [{
        'username': 'testuser',
        'verified': True,
        'public_metrics': {'followers_count': 3000}
    }]}
    return mock

def test_is_eligible_account():
    user = {'verified': True, 'public_metrics': {'followers_count': 3000}}
    assert is_eligible_account(user) is True
    
    user = {'verified': False, 'public_metrics': {'followers_count': 3000}}
    assert is_eligible_account(user) is False
    
    user = {'verified': True, 'public_metrics': {'followers_count': 1000}}
    assert is_eligible_account(user) is False

@patch('src.twitter_search.setup_twitter_client')
def test_find_relevant_twitter_accounts(mock_client, mock_twitter_response):
    mock_client.return_value.search_recent_tweets.return_value = mock_twitter_response
    token = {'name': 'Test', 'symbol': 'TEST'}
    
    accounts = find_relevant_twitter_accounts(token)
    assert len(accounts) == 1
    assert accounts[0]['username'] == 'testuser'