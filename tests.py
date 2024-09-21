import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
import re
from configparser import ConfigParser
from twikit import Client
from fastapi import HTTPException
from twitter_parse.utils import translate_message
from twitter_parse.utils import find_tweets
from twitter_parse.parse_tweet import tweet_get


@pytest_asyncio.fixture
def mock_tweet():
    return AsyncMock()

@pytest_asyncio.fixture
def mock_client():
    with patch('twikit.Client', autospec=True) as mock_client_class:
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.search_tweet = AsyncMock()
        mock_client_instance.load_cookies = AsyncMock()
        yield mock_client_instance


@pytest.mark.asyncio
async def test_find_tweets(mock_client, mock_tweet):
    mock_tweet_instance = AsyncMock()
    mock_tweet_instance.user.name = "Test User"
    mock_tweet_instance.text = "This is a test tweet"
    mock_tweet_instance.favorite_count = 123
    mock_client.search_tweet.return_value = [mock_tweet_instance]
    QUERY = "Test query"
    TWEETS = 1
    result = await find_tweets(QUERY, TWEETS)
    assert result != 0


@pytest.mark.asyncio
@patch('twitter_parse.utils.find_tweets')
async def test_tweet_get_no_tweets(mock_find_tweets):
    mock_find_tweets.return_value = []

    with pytest.raises(HTTPException) as excinfo:
        await tweet_get(query='wreklhgbrekhjbevkjdkvjfbnv', tweets=2, language='en')

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == 'No tweets found'
