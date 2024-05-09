import pytest

from main import Wallet


@pytest.fixture
def wallet():
    return Wallet()


@pytest.fixture
def temp_wallet_json(tmp_path):
    return tmp_path / "wallet.json"


@pytest.fixture
def temp_users_json(tmp_path):
    return tmp_path / "users.json"


@pytest.fixture
def wallet_deposit(wallet, temp_wallet_json):
    entry = dict(
        user="Test",
        category="deposit",
        amount=12345.0,
        description="test",
    )
    created_entry = wallet._write_to_file(**entry, path=temp_wallet_json)
    return created_entry


@pytest.fixture
def wallet_withdraw(wallet, temp_wallet_json):
    entry = dict(
        user="Test",
        category="withdraw",
        amount=12345.0,
        description="test",
    )
    created_entry = wallet._write_to_file(**entry, path=temp_wallet_json)
    return created_entry


@pytest.fixture
def authenticated_user(wallet, monkeypatch):
    monkeypatch.setattr(wallet, "user", "Test")
    monkeypatch.setattr(wallet, "authenticated", True)
    return "Test"


@pytest.fixture
def registered_user(wallet, temp_users_json):
    user_data = dict(
        user="Test_user",
        password="Test",
    )
    wallet.register(
        **user_data,
        path=temp_users_json
    )
    return user_data
