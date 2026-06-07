import os
from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio
from fastapi import HTTPException

os.environ.setdefault("MYSQL", "mysql+aiomysql://root:root@localhost:3306/test_social_media")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

from twitter_parse.utils import search_tweets
from twitter_parse.parse_tweet import tweet_get
from users import crud_users
from users.models import UpdateUser, UserLogin


class UserRow:
    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        password: str,
        avatar: bytes | None = None,
    ):
        self.id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.avatar = avatar

    def __getitem__(self, index: int):
        return (self.id, self.username, self.email, self.password, self.avatar)[index]

    def __len__(self):
        return 5


class SearchUserRow:
    def __init__(self, user_id: int, username: str, email: str):
        self.id = user_id
        self.username = username
        self.email = email


class FakeResult:
    def __init__(
        self,
        row: UserRow | None = None,
        rows: list[SearchUserRow] | None = None,
        scalar: bytes | None = None,
        lastrowid: int | None = None,
    ):
        self.row = row
        self.rows = rows or []
        self.scalar = scalar
        self.lastrowid = lastrowid

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.rows

    def scalar_one_or_none(self):
        return self.scalar


class FakeSession:
    def __init__(self, results: list[FakeResult]):
        self.results = results
        self.executed = []
        self.commit_count = 0

    async def execute(self, statement):
        self.executed.append(statement)
        return self.results.pop(0)

    async def commit(self):
        self.commit_count += 1


@pytest_asyncio.fixture
def mock_tweet():
    return AsyncMock()

@pytest_asyncio.fixture
def mock_client():
    with patch('twikit.Client', autospec=True) as mock_client_class:
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.search_tweet = AsyncMock()
        mock_client_instance.load_cookies = AsyncMock()
        yield mock_client_instance


@pytest.mark.asyncio
async def test_find_tweets(mock_client, mock_tweet):
    mock_tweet_instance = AsyncMock()
    mock_tweet_instance.user.name = "Test User"
    mock_tweet_instance.text = "This is a test tweet"
    mock_tweet_instance.favorite_count = 123
    mock_client.search_tweet.return_value = [mock_tweet_instance]
    QUERY = "Food"
    TWEETS = 10
    result = search_tweets(QUERY, TWEETS)
    assert result != 0


@pytest.mark.asyncio
@patch('twitter_parse.utils.search_tweets')
async def test_tweet_get_no_tweets(mock_find_tweets):
    mock_find_tweets.return_value = []

    with pytest.raises(HTTPException) as excinfo:
        await tweet_get(query='wreklhgbrekhjbevkjdkvjfbnv', tweets=2, language='en')

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == 'No tweets found'


@pytest.mark.asyncio
async def test_register_user_creates_user_with_hashed_password():
    session = FakeSession([
        FakeResult(row=None),
        FakeResult(lastrowid=7),
    ])

    with patch("users.crud_users.get_password_hash", return_value="hashed-password") as hash_password:
        response = await crud_users.register_user(
            username="tester",
            email="tester@example.com",
            password="password123",
            avatar=None,
            session=session,
        )

    hash_password.assert_called_once_with("password123")
    assert session.commit_count == 1
    assert response.id == 7
    assert response.username == "tester"
    assert response.email == "tester@example.com"
    assert response.password == "***********"


@pytest.mark.asyncio
async def test_register_user_rejects_duplicate_email():
    session = FakeSession([
        FakeResult(row=UserRow(1, "tester", "tester@example.com", "hashed-password")),
    ])

    with pytest.raises(HTTPException) as excinfo:
        await crud_users.register_user(
            username="tester",
            email="tester@example.com",
            password="password123",
            session=session,
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Email already registered"
    assert session.commit_count == 0


@pytest.mark.asyncio
async def test_login_user_returns_access_token_for_valid_credentials():
    session = FakeSession([
        FakeResult(row=UserRow(3, "tester", "tester@example.com", "hashed-password")),
    ])
    user_login = UserLogin(email="tester@example.com", password="password123")

    with (
        patch("users.crud_users.verify_password", return_value=True) as verify_password,
        patch("users.crud_users.create_access_token", return_value="access-token") as create_access_token,
    ):
        token = await crud_users.login_user(user_login, session=session)

    verify_password.assert_called_once_with("password123", "hashed-password")
    create_access_token.assert_called_once()
    assert token.access_token == "access-token"
    assert token.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_user_rejects_unknown_email():
    session = FakeSession([FakeResult(row=None)])
    user_login = UserLogin(email="missing@example.com", password="password123")

    with pytest.raises(HTTPException) as excinfo:
        await crud_users.login_user(user_login, session=session)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Incorrect email or password"


@pytest.mark.asyncio
async def test_get_current_user_info_includes_avatar_flag():
    session = FakeSession([FakeResult(scalar=b"avatar-bytes")])

    response = await crud_users.get_current_user_info(
        current_user={
            "id": 5,
            "username": "tester",
            "email": "tester@example.com",
            "password": "hashed-password",
        },
        session=session,
    )

    assert response.id == 5
    assert response.username == "tester"
    assert response.user_avatar is True


@pytest.mark.asyncio
async def test_search_users_returns_matching_users_except_current_user():
    session = FakeSession([
        FakeResult(rows=[
            SearchUserRow(2, "alice", "alice@example.com"),
            SearchUserRow(3, "bob", "bob@example.com"),
        ]),
    ])

    response = await crud_users.search_users(
        query="example",
        limit=10,
        current_user={"id": 1},
        session=session,
    )

    assert response == {
        "users": [
            {"id": 2, "username": "alice", "email": "alice@example.com"},
            {"id": 3, "username": "bob", "email": "bob@example.com"},
        ],
    }


@pytest.mark.asyncio
async def test_get_user_returns_masked_password_and_avatar_status():
    session = FakeSession([
        FakeResult(row=UserRow(4, "reader", "reader@example.com", "hashed-password", b"avatar")),
    ])

    response = await crud_users.get_user(user_id=4, session=session)

    assert response.id == 4
    assert response.username == "reader"
    assert response.email == "reader@example.com"
    assert response.password == "***************"
    assert response.user_avatar is True


@pytest.mark.asyncio
async def test_get_user_raises_404_when_user_does_not_exist():
    session = FakeSession([FakeResult(row=None)])

    with pytest.raises(HTTPException) as excinfo:
        await crud_users.get_user(user_id=404, session=session)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "There is no user with id 404"


@pytest.mark.asyncio
async def test_update_user_changes_profile_after_password_check():
    session = FakeSession([
        FakeResult(row=UserRow(8, "oldname", "old@example.com", "old-hash")),
        FakeResult(),
        FakeResult(row=UserRow(8, "newname", "new@example.com", "new-hash")),
    ])
    update_request = UpdateUser(
        new_username="newname",
        new_email="new@example.com",
        old_password="old-password",
        new_password="new-password",
    )

    with (
        patch("users.crud_users.verify_password", return_value=True) as verify_password,
        patch("users.crud_users.get_password_hash", return_value="new-hash") as hash_password,
    ):
        response = await crud_users.update_user(
            user_upd=update_request,
            current_user={"id": 8},
            session=session,
        )

    verify_password.assert_called_once_with("old-password", "old-hash")
    hash_password.assert_called_once_with("new-password")
    assert session.commit_count == 1
    assert response.id == 8
    assert response.username == "newname"
    assert response.email == "new@example.com"
    assert response.password == "********"


@pytest.mark.asyncio
async def test_update_user_rejects_wrong_old_password():
    session = FakeSession([
        FakeResult(row=UserRow(8, "oldname", "old@example.com", "old-hash")),
    ])
    update_request = UpdateUser(old_password="wrong-password")

    with patch("users.crud_users.verify_password", return_value=False):
        with pytest.raises(HTTPException) as excinfo:
            await crud_users.update_user(
                user_upd=update_request,
                current_user={"id": 8},
                session=session,
            )

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Wrong password!"
    assert session.commit_count == 0


@pytest.mark.asyncio
async def test_delete_user_deletes_current_user():
    session = FakeSession([FakeResult()])

    response = await crud_users.delete_user(
        current_user={"id": 10},
        session=session,
    )

    assert response == {"message": "User successfully deleted"}
    assert session.commit_count == 1
