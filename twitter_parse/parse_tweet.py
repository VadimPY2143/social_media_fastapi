from fastapi import APIRouter, Depends
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session
from database import twitter_parse_table, engine
from .utils import tweet_get
from .models import Tweet
import asyncio

router = APIRouter(
    tags=['Twitter'],
    prefix='/twitter'
)


@router.get('/tweet/get')
async def get_tweet(tweet: Tweet = Depends()) -> dict:
    try:
        response = await tweet_get(query=tweet.query, tweets=tweet.tweets, language=tweet.lang)
        with Session(engine) as session:
            for tweet_data in response.values():
                stmt = insert(twitter_parse_table).values(
                    query=tweet.query,
                    tweet_text= tweet_data.get('tweet_text'),
                    tweet_likes=tweet_data.get('likes'),
                    created_at=tweet_data.get('created_at'),
                    tweet_id=tweet_data.get('post_id'),
                    author_id=tweet_data.get('author_id'),
                )
                session.execute(stmt)
            session.commit()
    except Exception as e:
        response = {'error': str(e)}
    return response

