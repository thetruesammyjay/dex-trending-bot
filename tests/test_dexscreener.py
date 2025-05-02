import pytest
from unittest.mock import patch, Mock
from src.dexscreener import get_top_trending_tokens

@patch('src.dexscreener.requests.get')
def test_get_top_trending_tokens(mock_get):
    # Setup mock response
    mock_response = Mock()
    mock_response.text = """
    <html>
        <div class="trending-item">
            <span class="token-name">Test Token</span>
            <span class="token-symbol">TEST</span>
        </div>
    </html>
    """
    mock_get.return_value = mock_response
    
    # Test function
    tokens = get_top_trending_tokens()
    
    # Assertions
    assert len(tokens) > 0
    assert tokens[0]['name'] == "Test Token"
    assert tokens[0]['symbol'] == "TEST"