import asyncio
import re
from fastapi import HTTPException
from translate import Translator
from dotenv import load_dotenv
import os
import requests

load_dotenv()

BEARER = os.getenv('BEARER')



def translate_message(message: str, language: str) -> str:
    if language:
        translator = Translator(to_lang=language)
        translation = translator.translate(message)
        return translation
    return message



def search_tweets(query: str, tweets: int = 10):
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {BEARER}"}
    params = {
        "query": query,
        "tweet.fields": "author_id,created_at,public_metrics",
        "max_results": tweets,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    return response.json()



async def tweet_get(query: str, language: str, tweets: int = 10):
    if tweets <= 0:
        raise HTTPException(status_code=400, detail='Number of tweets must be more than 0')
    posts = search_tweets(query, tweets)

    if posts:
        result_dict = {
            index + 1: {
                'tweet_text': translate_message(post.get('text'), language),
                'likes': post.get('public_metrics').get('like_count'),
                'created_at': post.get('created_at'),
                'post_id': post.get('id'),
                'author_id': post.get('author_id'),
            }
            for index, post in enumerate(posts['data'])
        }
        return result_dict
    else:
        raise HTTPException(status_code=404, detail='No tweets found')

