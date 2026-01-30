from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, Text, BigInteger, DateTime
from sqlalchemy.dialects.mysql import MEDIUMBLOB
from datetime import datetime
import os

load_dotenv()

async_url = os.getenv('MYSQL')
engine = create_async_engine(async_url, echo=True)
metadata = MetaData()


post_table = Table(
    'posts',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('post_name', String(50)),
    Column('author', ForeignKey('users.id')),
    Column('text', String(3000)),
    Column('picture', MEDIUMBLOB, nullable=True),
    Column('is_approved', Integer, default=1),
)


user_table = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(15), nullable=False, unique=True),
    Column('email', String(100), nullable=False),
    Column('password', String(255), nullable=False),
    Column('avatar', MEDIUMBLOB, nullable=True)
)

twitter_parse_table = Table(
    'twitter_parse',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('query', String(100)),
    Column('tweet_text', Text),
    Column('tweet_likes', Integer),
    Column('created_at', String(100), nullable=False),
    Column('tweet_id', BigInteger, nullable=False),
    Column('author_id', BigInteger, nullable=False),
)

comment_table = Table(
    'comments',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('post_id', ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
    Column('user_id', ForeignKey('users.id'), nullable=False),
    Column('text', String(500), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
)


reply_comments_table = Table(
    'reply_comments',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('comment_id', ForeignKey('comments.id', ondelete='CASCADE'), nullable=False),
    Column('user_id', ForeignKey('users.id'), nullable=False),
    Column('text', String(500), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
)


post_likes_table = Table(
    'post_likes',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('post_id', ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
)

comment_likes_table = Table(
    'comment_likes',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('comment_id', ForeignKey('comments.id', ondelete='CASCADE'), nullable=False),
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
)

followers_table = Table(
    'followers',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('follower_id', ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('following_id', ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
)

chat_table = Table(
    'chat',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
)

message_table = Table(
    'messages',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('chat_id', ForeignKey('chat.id', ondelete='CASCADE'), nullable=False),
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('message', String(500), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
