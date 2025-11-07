from fastapi import FastAPI, Request
from posts.crud_posts import router as post_router
from twitter_parse.parse_tweet import router as twitter_router
from users.crud_users import router as user_router
from comments.crud_comments import router as comment_router
from likes.crud_likes import router as likes_router
from followers.crud_followers import router as followers_router


app = FastAPI()
app.include_router(user_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(twitter_router)
app.include_router(likes_router)
app.include_router(followers_router)

