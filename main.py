from fastapi import FastAPI
from posts.crud_posts import router as post_router
from twitter_parse.parse_tweet import router as twitter_router
from users.crud_users import router as user_router


app = FastAPI()
app.include_router(user_router)
app.include_router(post_router)
app.include_router(twitter_router)


