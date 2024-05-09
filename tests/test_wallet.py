class TestWallet:

    def test_registration(self, wallet, temp_users_json):
        assert wallet.register(
            "Test_User",
            "Test_Password",
            path=temp_users_json
        ) == "Test_User"

    def test_user_already_exists(
            self,
            wallet,
            registered_user,
            temp_users_json
    ):
        assert wallet.register(
            **registered_user,
            path=temp_users_json
        ) == ("Такой пользователь уже существует,"
              " пожалуйста, попробуйте ещё раз.")

    def test_valid_auth(
            self,
            registered_user,
            wallet,
            temp_users_json
    ):
        assert wallet.auth(
            **registered_user,
            path=temp_users_json
        ) == "Test_user"

    def test_auth_invalid_credentials(
            self,
            wallet,
            temp_users_json,
            registered_user
    ):
        assert wallet.auth(
            "Test_123432",
            "Test_2",
            path=temp_users_json
        ) == "Неверные имя пользователя или пароль"

    def test_unlogged_user_cannot_use_commands(self, wallet, monkeypatch):
        monkeypatch.setattr(wallet, "authenticated", False)
        monkeypatch.setattr("builtins.input", lambda _: "balance")
        assert wallet.get_balance("Test_User") == "Вы не вошли в систему"

    def test_add_transaction(
            self,
            wallet,
            temp_wallet_json,
            authenticated_user
    ):
        assert wallet.run_transaction(
            _type="deposit",
            amount="12345",
            description="test_text",
            path=temp_wallet_json
        ) is True

    def test_user_cannot_deposit_non_integer(
            self,
            wallet,
            authenticated_user,
            temp_wallet_json
    ):
        assert wallet.run_transaction(
            _type="deposit",
            amount="test_text",
            description="test_text",
            path=temp_wallet_json

        ) is False

    def test_write_transaction_to_file(
            self,
            wallet,
            wallet_deposit,
            temp_wallet_json
    ):
        with open(temp_wallet_json, "r") as file:
            lines = file.readlines()
            assert len(lines) > 0

    def test_get_full_history(
            self,
            wallet,
            wallet_deposit,
            wallet_withdraw,
            temp_wallet_json,
            authenticated_user
    ):
        history = wallet.print_history(mode="all", history=wallet._get_history(
            path=temp_wallet_json,
            user=authenticated_user
        ))
        assert "Доход" in history and "Расход" in history

    def test_get_deposit_history(
            self,
            wallet,
            wallet_deposit,
            wallet_withdraw,
            temp_wallet_json,
            authenticated_user
    ):
        history = wallet.print_history(mode="deposit",
                                       history=wallet._get_history(
                                           path=temp_wallet_json,
                                           user=authenticated_user
                                       ))
        assert "Доход" in history and "Расход" not in history

    def test_get_withdraw_history(
            self,
            wallet,
            wallet_deposit,
            wallet_withdraw,
            monkeypatch,
            temp_wallet_json,
            authenticated_user
    ):
        history = wallet.print_history(mode="withdraw",
                                       history=wallet._get_history(
                                           path=temp_wallet_json,
                                           user=authenticated_user
                                       ))
        assert "Расход" in history and "Доход" not in history

    def test_get_history_unknown_mode(
            self,
            wallet,
            wallet_deposit,
            wallet_withdraw,
            monkeypatch,
            temp_wallet_json,
            authenticated_user
    ):
        history = wallet.print_history(
            mode="randommode",
            history=wallet._get_history(
                path=temp_wallet_json,
                user=authenticated_user
            )
        )
        assert history == "Неизвестный режим"

    def test_empty_history(self, wallet, authenticated_user):
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
            authenticated_user
    ):
        assert wallet.get_balance(
            history=wallet._get_history(
                user=authenticated_user,
                path=temp_wallet_json
            )
        ) == (f"Ваш текущий баланс: {wallet_deposit[0]['amount']}\n\n"
              f"Доходы: {wallet_deposit[0]['amount']}, Расходы: 0.0")

    def test_get_balance_unknown_user(
            self,
            wallet,
            monkeypatch,
            authenticated_user,
            wallet_deposit,
            temp_wallet_json
    ):
        assert wallet.get_balance(
            history=wallet._get_history(
                user="Unknown",
                path=temp_wallet_json
            )
        ) == "Ваш текущий баланс: 0.0\n\nДоходы: 0.0, Расходы: 0.0"

    def test_get_balance_no_history(
            self,
            wallet,
            authenticated_user
    ):
        assert wallet.get_balance(history=[]) == (
            "Ваш текущий баланс: 0.0\n\n"
            "Доходы: 0.0, Расходы: 0.0"
        )

    def test_invalid_search(
            self,
            wallet,
            temp_wallet_json,
            wallet_deposit,
            authenticated_user
    ):
        assert wallet.search(
            mode="1",
            user_input="test",
            history=wallet._get_history(
                user=authenticated_user,
                path=temp_wallet_json
            )
        ) == "Ничего не найдено"

    def test_valid_search(
            self,
            wallet,
            temp_wallet_json,
            wallet_deposit,
            authenticated_user
    ):
        search_result = wallet.search(
            mode="amount",
            user_input="100",
            history=[
                {"date": "2022-01-01", "category": "deposit", "amount": 100.0,
                 "description": "Groceries"},
                {"date": "2022-01-02", "category": "withdraw", "amount": 200.0,
                 "description": "Gas"},
            ]
        )
        assert search_result is not None
        assert "100.0" in search_result and "200.0" not in search_result
        second_search_res = wallet.search(
            mode="category",
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

    def test_edit_transaction_correct_values(
            self,
            wallet,
            temp_wallet_json,
            authenticated_user,
            wallet_deposit,
            monkeypatch
    ):
        valid_responses = iter(["2024-09-05", "deposit", "100", "description"])
        monkeypatch.setattr("builtins.input", lambda _: next(valid_responses))
        edited_transaction = wallet.edit_transaction(
            user=authenticated_user,
            path=temp_wallet_json,
            transaction_id=wallet_deposit[0]["id"],
        )
        assert edited_transaction is True

    def test_edit_transaction_incorrect_date(
            self,
            wallet,
            temp_wallet_json,
            authenticated_user,
            wallet_deposit,
            monkeypatch
    ):
        invalid_responses = iter(["0000-00-35", "deposit", "100", "description"])
        monkeypatch.setattr("builtins.input", lambda _: next(invalid_responses))
        edited_transaction = wallet.edit_transaction(
            user=authenticated_user,
            path=temp_wallet_json,
            transaction_id=wallet_deposit[0]["id"],
        )
        assert edited_transaction is False

    def test_edit_transaction_incorrect_amount(
            self,
            wallet,
            temp_wallet_json,
            authenticated_user,
            wallet_deposit,
            monkeypatch
    ):
        invalid_responses = iter(["2024-09-05", "deposit", "test", "description"])
        monkeypatch.setattr("builtins.input", lambda _: next(invalid_responses))
        edited_transaction = wallet.edit_transaction(
            user=authenticated_user,
            path=temp_wallet_json,
            transaction_id=wallet_deposit[0]["id"],
        )
        assert edited_transaction is False

    def test_edit_transaction_incorrect_description(
            self,
            wallet,
            temp_wallet_json,
            authenticated_user,
            wallet_deposit,
            monkeypatch
    ):
        invalid_responses = iter(["2024-09-05", "deposit", "100", "test" * 100])
        monkeypatch.setattr("builtins.input", lambda _: next(invalid_responses))
        edited_transaction = wallet.edit_transaction(
            user=authenticated_user,
            path=temp_wallet_json,
            transaction_id=wallet_deposit[0]["id"],
        )
        assert edited_transaction is False

    def test_edit_transaction_incorrect_category(
            self,
            wallet,
            temp_wallet_json,
            authenticated_user,
            wallet_deposit,
            monkeypatch
    ):
        invalid_responses = iter(["2024-09-05", "test", "100", "description"])
        monkeypatch.setattr("builtins.input", lambda _: next(invalid_responses))
        edited_transaction = wallet.edit_transaction(
            user=authenticated_user,
            path=temp_wallet_json,
            transaction_id=wallet_deposit[0]["id"],
        )
        assert edited_transaction is False
