from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, LargeBinary, ForeignKey, Text, BigInteger

engine = create_engine('mysql+pymysql://root:@localhost:3306/Social_media', echo=True)
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

metadata.create_all(engine)
