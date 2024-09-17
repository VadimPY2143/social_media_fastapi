from fastapi import APIRouter
from .utils import tweet_get


router = APIRouter(
    tags=['Twitter'],
    prefix='/twitter'
)


@router.get('/tweet/get')
async def get_tweet(query: str, tweets: int, language: str) -> dict:
    return await tweet_get(query=query, tweets=tweets, language=language)
