import pytest

from main import Wallet


@pytest.fixture
def wallet():
    return Wallet()


@pytest.fixture()
def authenticated_user(wallet, monkeypatch):
    monkeypatch.setattr(wallet, "authenticated", True)
