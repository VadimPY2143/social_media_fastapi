from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, LargeBinary

engine = create_engine('sqlite+pysqlite:///post.db', echo=True)
metadata = MetaData()


post_table = Table(
    'posts',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('post_name', String(20)),
    Column('author', String(20)),
    Column('text', String(100)),
    Column('picture', LargeBinary, nullable=True),
)


user_table = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(15), nullable=False),
    Column('email', String(50), nullable=False),
    Column('password', String(40), nullable=False)
)

metadata.create_all(engine)
