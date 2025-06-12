from fastapi import APIRouter, Depends
from .utils import tweet_get
from .models import Tweet

router = APIRouter(
    tags=['Twitter'],
    prefix='/twitter'
)


@router.get('/tweet/get')
async def get_tweet(tweet: Tweet = Depends()) -> dict:
    return await tweet_get(query=tweet.query, tweets=tweet.tweets, language=tweet.lang)
