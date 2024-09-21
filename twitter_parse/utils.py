from configparser import ConfigParser
from twikit import Client
from fastapi import HTTPException
import re
from translate import Translator

config = ConfigParser()
config.read('twitter_parse/config.ini')
username = config['X']['username']
email = config['X']['email']
password = config['X']['password']


def translate_message(message: str, language: str) -> str:
    if language:
        translator = Translator(to_lang=language)
        translation = translator.translate(message)
        return translation
    return message


async def find_tweets(QUERY: str, TWEETS: int = 1) -> list:
    tweets_result = []
    client = Client(language='en-US')
    client.load_cookies('twitter_parse/cookies.json')
    tweets = await client.search_tweet(QUERY, product='Top')
    tweet_count = 0
    for tweet in tweets:
        if TWEETS != tweet_count:
            tweet_count += 1
            tweet_data = [tweet.user.name, tweet.text, tweet.favorite_count]
            tweets_result.append(tweet_data)
    return tweets_result


async def tweet_get(query: str, tweets: int, language: str):
    if tweets <= 0:
        raise HTTPException(status_code=400, detail='Number of tweets must be more than 0')
    post = await find_tweets(QUERY=query, TWEETS=tweets)
    if len(post) != 0:
        result_dict = {
            index + 1: {
                'tweet_name': translate_message(item[0], language),
                'tweet_text': re.sub(r'http\S+$', '', translate_message(item[1], language)).strip(),
                'tweet_image': item[1].split()[-1] if 'https' in item[1].split()[-1] else 'no image',
                'likes': item[2]
            }
            for index, item in enumerate(post)
        }
        return result_dict
    raise HTTPException(status_code=404, detail='No tweets found')




