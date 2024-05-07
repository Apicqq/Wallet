import datetime
import getpass

import pytest


class TestWallet:

    def test_registration(self, wallet, monkeypatch, temp_users_json):
        monkeypatch.setattr("builtins.input", lambda _: "register")
        monkeypatch.setattr("builtins.input", lambda _: "TestUserOne")
        monkeypatch.setattr(getpass, "getpass", lambda _: "Test")
        assert wallet.register(path=temp_users_json) == "TestUserOne"
        monkeypatch.setattr("builtins.input", lambda _: "register")
        monkeypatch.setattr("builtins.input", lambda _: "TestUserOne")
        monkeypatch.setattr(getpass, "getpass", lambda _: "Test")
        assert wallet.register(path=temp_users_json) == (
            "Такой пользователь уже существует. "
            "Пожалуйста, попробуйте ещё раз."
        )

    @pytest.mark.parametrize(
        "user, password",
        [("Test", "Test")]
    )
    def test_auth(self,
                  user, password, monkeypatch, wallet):
        monkeypatch.setattr("builtins.input", lambda _: "auth")
        monkeypatch.setattr("builtins.input", lambda _: user)
        monkeypatch.setattr(getpass, "getpass", lambda _: password)
        assert wallet.auth() == user

    def test_unlogged_user_cannot_use_commands(self, wallet, monkeypatch):
        monkeypatch.setattr(wallet, "authenticated", False)
        monkeypatch.setattr("builtins.input", lambda _: "balance")
        assert wallet.get_balance("Test_User") == "Вы не вошли в систему"

    def test_add_transaction(self, wallet, monkeypatch):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr("builtins.input", lambda _: "deposit")
        monkeypatch.setattr("builtins.input", lambda _: "12345")
        assert wallet.run_transaction("deposit") is True

    def test_user_cannot_deposit_non_integer(self, wallet, monkeypatch):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr("builtins.input", lambda _: "deposit")
        monkeypatch.setattr("builtins.input", lambda _: "test_text")
        assert wallet.run_transaction("deposit") is False

    def test_write_transaction_to_file(self, wallet, wallet_deposit,
                                       temp_wallet_json):
        with open(temp_wallet_json, "r") as file:
            lines = file.readlines()
            assert len(lines) > 0

    def test_internal_get_history(
            self,
            wallet,
            monkeypatch,
            temp_wallet_json,
            wallet_deposit
    ):
        data = {
            "user": "Test",
            "date": datetime.datetime.now().date().isoformat(),
            "category": "deposit",
            "amount": 12345.0,
            "description": "test"
        }
        monkeypatch.setattr(wallet, "authenticated", True)
        history = wallet._get_history(user="Test", path=temp_wallet_json)
        assert len(list(history)) > 0
        assert data in list(history)

    def test_get_full_history(
            self,
            wallet,
            wallet_deposit,
            wallet_withdraw,
            monkeypatch,
            temp_wallet_json
    ):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr(wallet, "user", "Test")
        history = wallet.print_history(mode="all", history=wallet._get_history(
            path=temp_wallet_json,
            user="Test"
        ))
        assert "Доход" in history and "Расход" in history

    def test_get_deposit_history(
            self,
            wallet,
            wallet_deposit,
            wallet_withdraw,
            monkeypatch,
            temp_wallet_json
    ):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr(wallet, "user", "Test")
        history = wallet.print_history(mode="deposit",
                                       history=wallet._get_history(
                                           path=temp_wallet_json,
                                           user="Test"
                                       ))
        assert "Доход" in history and "Расход" not in history

    def test_get_withdraw_history(
            self,
            wallet,
            wallet_deposit,
            wallet_withdraw,
            monkeypatch,
            temp_wallet_json
    ):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr(wallet, "user", "Test")
        history = wallet.print_history(mode="withdraw",
                                       history=wallet._get_history(
                                           path=temp_wallet_json,
                                           user="Test"
                                       ))
        assert "Доход" not in history and "Расход" not in history

    def test_get_history_unknown_mode(
            self,
            wallet,
            wallet_deposit,
            wallet_withdraw,
            monkeypatch,
            temp_wallet_json
    ):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr(wallet, "user", "Test")
        history = wallet.print_history(
            mode="randommode",
            history=wallet._get_history(
                path=temp_wallet_json,
                user="Test"
            )
        )
        assert history == "Неизвестный режим"

    def test_empty_history(self, wallet, monkeypatch):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr("builtins.input", lambda _: "history")
        monkeypatch.setattr("builtins.input", lambda _: "all")
        history = wallet.print_history(
            mode="all",
            history=[]
        )
        assert history == "Ничего не найдено"

    def test_get_balance(
            self,
            wallet,
            wallet_deposit,
            temp_wallet_json,
            monkeypatch
    ):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr("builtins.input", lambda _: "balance")
        assert wallet.get_balance(
            history=wallet._get_history(
                user="Test",
                path=temp_wallet_json
            )
        ) == "Ваш текущий баланс: 12345.0"

    def test_get_balance_unknown_user(self, wallet, monkeypatch,
                                      wallet_deposit,
                                      temp_wallet_json):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr("builtins.input", lambda _: "balance")
        assert wallet.get_balance(
            history=wallet._get_history(
                user="Unknown",
                path=temp_wallet_json
            )
        ) == "Ваш текущий баланс: 0.0"

    def test_get_balance_no_history(self, wallet, monkeypatch):
        monkeypatch.setattr(wallet, "authenticated", True)
        monkeypatch.setattr("builtins.input", lambda _: "balance")
        assert wallet.get_balance(history=[]) == "Ваш текущий баланс: 0.0"

    def test_invalid_search(
            self,
            wallet,
            monkeypatch,
            temp_wallet_json,
            wallet_deposit
    ):
        monkeypatch.setattr(wallet, "authenticated", True)
        assert wallet.search(
            mode="1",
            user_input="test",
            history=wallet._get_history(
                user="Test",
                path=temp_wallet_json
            )
        ) == "Ничего не найдено"

    def test_valid_search(
            self,
            wallet,
            temp_wallet_json,
            wallet_deposit,
            monkeypatch
    ):
        monkeypatch.setattr(wallet, "authenticated", True)
        search_result = wallet.search(
            mode="Сумма",
            user_input="100",
            history=[
                {"date": "2022-01-01", "category": "deposit", "amount": 100.0,
                 "description": "Groceries"},
                {"date": "2022-01-02", "category": "withdraw", "amount": 200.0,
                 "description": "Gas"},
            ]
        )
        assert search_result is not None
        assert "100.0" in search_result
        assert "200.0" not in search_result
        second_search_res = wallet.search(
            mode="Категория",
            user_input="deposit",
            history=[
                {"date": "2022-01-01", "category": "deposit", "amount": 100.0},
                {"date": "2022-01-02", "category": "withdraw",
                 "amount": 200.0},
                {"date": "2022-01-03", "category": "deposit", "amount": 300.0},
            ]
        )
        assert second_search_res is not None
        assert ("Доход" in second_search_res and
                "Расход" not in second_search_res)

    def test_edit_transaction(self, wallet, temp_wallet_json):
        pass
