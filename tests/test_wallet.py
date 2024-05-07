import getpass

import pytest


class TestWallet:
    @pytest.mark.parametrize(
        "user, password, expected",
        [("Test", "Test", True)]
    )
    def test_auth(self,
                  user, password, expected, monkeypatch, wallet):
        monkeypatch.setattr("builtins.input", lambda _: "auth")
        monkeypatch.setattr("builtins.input", lambda _: user)
        monkeypatch.setattr(getpass, "getpass", lambda _: password)
        assert wallet.auth() == user

    def test_unlogged_user_cannot_use_commands(self, wallet, monkeypatch):
        monkeypatch.setattr(wallet, "authenticated", False)
        monkeypatch.setattr("builtins.input", lambda _: "balance")
        assert wallet.get_balance("Test_User") == "Вы не вошли в систему"

    def test_empty_history(self, wallet, monkeypatch):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr("builtins.input", lambda _: "history")
        monkeypatch.setattr("builtins.input", lambda _: "all")
        assert wallet.print_history() == "Ничего не найдено"

    def test_cannot_pass_non_integers_to_deposits(self, wallet, monkeypatch):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr("builtins.input", lambda _: "deposit")
        monkeypatch.setattr("builtins.input", lambda _: "test_text")
        assert wallet.run_transaction("deposit") is False
