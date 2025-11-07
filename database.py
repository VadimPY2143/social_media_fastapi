from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, LargeBinary, ForeignKey, Text, BigInteger, DateTime
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv('MYSQL'), echo=True)
metadata = MetaData()


post_table = Table(
    'posts',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('post_name', String(20)),
    Column('author', ForeignKey('users.id')),
    Column('text', String(100)),
    Column('picture', LargeBinary, nullable=True),
)


user_table = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(15), nullable=False, unique=True),
    Column('email', String(50), nullable=False),
    Column('password', String(40), nullable=False),
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
    Column('post_id', ForeignKey('posts.id'), nullable=False),
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

metadata.create_all(engine)
