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



def search_tweets(query: str, tweets: int = 10, language: str = None):
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

# print(search_tweets("health"))



async def tweet_get(query: str, tweets: int, language: str):
    if tweets <= 0:
        raise HTTPException(status_code=400, detail='Number of tweets must be more than 0')
    posts = search_tweets(query=query, tweets=tweets, language=language)

    if len(posts) != 0:
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
    raise HTTPException(status_code=404, detail='No tweets found')


# asyncio.run(tweet_get("health", 10, "en"))
# posts = {'data': [{'public_metrics': {'retweet_count': 0, 'reply_count': 0, 'like_count': 0, 'quote_count': 0,
#                                       'bookmark_count': 0, 'impression_count': 0},
#                    'edit_history_tweet_ids': ['1932847100116566296'], 'created_at': '2025-06-11T17:07:13.000Z',
#                    'author_id': '277138708',
#                    'text': 'In a noisy, high-stakes B2B market, how do you arm your sales force to win? The latest Health Marketing Collective podcast episode is full of bold takes, practical insight, and just the right amount of fire. 🎧 https://t.co/eI9lloQGvh https://t.co/71FMLbTGgo',
#                    'id': '1932847100116566296'}, {
#                       'public_metrics': {'retweet_count': 158, 'reply_count': 0, 'like_count': 0, 'quote_count': 0,
#                                          'bookmark_count': 0, 'impression_count': 0},
#                       'edit_history_tweet_ids': ['1932847099772535238'], 'created_at': '2025-06-11T17:07:13.000Z',
#                       'author_id': '2851039425',
#                       'text': 'RT @htmljones: hi mtf here! detransitioning bc i wasn’t medically gatekept enough ):  but if u don’t use my new feminine chosen name i will…',
#                       'id': '1932847099772535238'}, {
#                       'public_metrics': {'retweet_count': 0, 'reply_count': 0, 'like_count': 0, 'quote_count': 0,
#                                          'bookmark_count': 0, 'impression_count': 0},
#                       'edit_history_tweet_ids': ['1932847099600683381'], 'created_at': '2025-06-11T17:07:13.000Z',
#                       'author_id': '815950062069121025',
#                       'text': '10 years after my daughter Alice’s preventable death, NELFT &amp; a ward manager have been convicted of criminal Health &amp; Safety offences. The Met’s press release outlines their investigation &amp; some of the many details of how Alice was so abysmally failed:\n\nhttps://t.co/mXAf63gQdQ',
#                       'id': '1932847099600683381'}, {
#                       'public_metrics': {'retweet_count': 0, 'reply_count': 0, 'like_count': 0, 'quote_count': 0,
#                                          'bookmark_count': 0, 'impression_count': 0},
#                       'edit_history_tweet_ids': ['1932847098413601022'], 'created_at': '2025-06-11T17:07:13.000Z',
#                       'author_id': '938448624962355201',
#                       'text': "Yikes\nAnother step closer …\n\nH5N1 bird flu 'capable of airborne transmission' https://t.co/VHJoDPGP46",
#                       'id': '1932847098413601022'}, {
#                       'public_metrics': {'retweet_count': 65, 'reply_count': 0, 'like_count': 0, 'quote_count': 0,
#                                          'bookmark_count': 0, 'impression_count': 0},
#                       'edit_history_tweet_ids': ['1932847098065567787'], 'created_at': '2025-06-11T17:07:13.000Z',
#                       'author_id': '1667569839286747136',
#                       'text': "RT @Rethink_: 👏 Great to see this initiative from our friends at @YoungMindsUK. \n\nThere is a crisis in children's mental health.\n\n💙 Togethe…",
#                       'id': '1932847098065567787'}, {
#                       'public_metrics': {'retweet_count': 987, 'reply_count': 0, 'like_count': 0, 'quote_count': 0,
#                                          'bookmark_count': 0, 'impression_count': 0},
#                       'edit_history_tweet_ids': ['1932847093955149924'], 'created_at': '2025-06-11T17:07:12.000Z',
#                       'author_id': '1357565045476065284',
#                       'text': 'RT @MustStopMurad: Stay HUMBLE.\nStay MODEST.\nStay STOIC.\nDO NOT celebrate.\nThere is 6-12 months of *this* to go.\nAnd that’s just the local…',
#                       'id': '1932847093955149924'}, {
#                       'public_metrics': {'retweet_count': 0, 'reply_count': 0, 'like_count': 0, 'quote_count': 0,
#                                          'bookmark_count': 0, 'impression_count': 0},
#                       'edit_history_tweet_ids': ['1932847093863063819'], 'created_at': '2025-06-11T17:07:12.000Z',
#                       'author_id': '1774732936014700544',
#                       'text': 'Thanks for your love and support ❤️ \n\nThey\'re kids without education, health that needs screening, communities with no construction, and animals who needs care and food \n\nWe have to come together let\'s make our world a better place \nType "YES " to proceed \n\nSigned:\nELON MUSK ★ https://t.co/jvjaM1sp6M',
#                       'id': '1932847093863063819'}, {
#                       'public_metrics': {'retweet_count': 28, 'reply_count': 0, 'like_count': 0, 'quote_count': 0,
#                                          'bookmark_count': 0, 'impression_count': 0},
#                       'edit_history_tweet_ids': ['1932847092315148692'], 'created_at': '2025-06-11T17:07:12.000Z',
#                       'author_id': '39145861',
#                       'text': 'RT @dr_andrealove: The erosion of trust in vaccines, health agencies, and scientific institutions is an intentional, well-funded, and coord…',
#                       'id': '1932847092315148692'}, {
#                       'public_metrics': {'retweet_count': 202, 'reply_count': 0, 'like_count': 0, 'quote_count': 0,
#                                          'bookmark_count': 0, 'impression_count': 0},
#                       'edit_history_tweet_ids': ['1932847091442987327'], 'created_at': '2025-06-11T17:07:11.000Z',
#                       'author_id': '131556443',
#                       'text': 'RT @NoaGresiva: Me pasan un ensayo analítico, revisado y publicado en la revista científica American Journal of Public Health, sobre la sal…',
#                       'id': '1932847091442987327'}, {
#                       'public_metrics': {'retweet_count': 55, 'reply_count': 0, 'like_count': 0, 'quote_count': 0,
#                                          'bookmark_count': 0, 'impression_count': 0},
#                       'edit_history_tweet_ids': ['1932847091426210027'], 'created_at': '2025-06-11T17:07:11.000Z',
#                       'author_id': '1667569839286747136',
#                       'text': "RT @Rethink_: 🗓️ Our bi-annual Members' day is on 16 November 2024.\n\nKeynote speaker @zoe_swithenbank will share research on different trea…",
#                       'id': '1932847091426210027'}],
#          'meta': {'newest_id': '1932847100116566296', 'oldest_id': '1932847091426210027', 'result_count': 10,
#                   'next_token': 'b26v89c19zqg8o3fsc56q8nxth3v73yy2pg3keuna2jy5'}}
#
# for index, post in enumerate(posts['data']):
#     print(post.get('author_id'))
#     break
# for index, post in :
#     print(post)