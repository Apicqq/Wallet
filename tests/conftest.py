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
    wallet._write_to_file(**entry, path=temp_wallet_json)
    return entry


@pytest.fixture
def wallet_withdraw(wallet, temp_wallet_json):
    entry = dict(
        user="Test",
        category="withdraw",
        amount=12345.0,
        description="test",
    )
    wallet._write_to_file(**entry, path=temp_wallet_json)
    return entry
