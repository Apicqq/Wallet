import json
import re
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Union
from uuid import uuid4

from constants import (
    UtilityConstants as Uc,
    Literals as Lit,
    ErrorLiterals as Err,
    TRANSACTION_FIELDS_MAPPING,
    DEPOSIT_TYPE_MAPPING,
)
from decorators import restricted
from mask_input import mask_input


class Wallet:
    def __init__(self):
        self.user = None
        self.authenticated = False
        self.first_time_logged = True
        self.required_to_show_commands = True

    @restricted
    def run_transaction(
            self,
            amount: str,
            description: str = None,
            _type: str = "deposit",
            path: Union[str, Path] = Uc.WALLETS_LOCATION,
    ) -> bool:
        """
        Провести транзакцию. Возвращает True, если транзакция была
        выполнена, False в противном случае.

        :param description: Описание транзакции.
        :param _type: Тип транзакции, по умолчанию deposit.
        :param path: Путь к файлу с историей транзакций, по умолчанию
         указывает на файл wallets.json в корневой папке.
        :param amount: Сумма транзакции в виде строки.
        :returns: True если транзакция была выполнена, False в ином случае.
        """
        try:
            amount = float(amount)
        except ValueError:
            print(Err.INVALID_NUMBER)
            return False
        if _type == "deposit":
            self._write_to_file(
                self.user,
                amount,
                category="deposit",
                description=description,
                path=path,
            )
        elif _type == "withdraw":
            self._write_to_file(
                self.user,
                amount,
                category="withdraw",
                description=description,
                path=path,
            )
        print(
            f"{Lit.TRANSACTION_ACCEPTED}"
            f"{self.get_balance(self._get_history(self.user))}"
        )
        return True

    @staticmethod
    def _get_history(
            user: str,
            path: Union[str, Path] = Uc.WALLETS_LOCATION
    ) -> list[dict]:
        """
        Получить историю транзакций пользователя. Метод не должен
        использоваться внешними модулями, вместо этого используйте
        print_history().

        :param user: Пользователь, для которого нужно получить историю.
        :param path: Путь к файлу с историей транзакций, по умолчанию
         указывает на файл wallets.json в корневой папке.
        :returns: List[dict] - история транзакций.
        """
        with open(path, "r") as file:
            data = json.loads(file.read())
            return [item for item in data if item["user"] == user]

    @staticmethod
    def _get_transaction_by_id(
            user: str,
            transaction_id: str,
            path: Union[str, Path] = Uc.WALLETS_LOCATION,
    ) -> Union[dict, bool]:
        """
        Возвращает транзакцию по id, если она существует. В ином случае
         возвращает False.
        :param user: Пользователь, для которого нужно получить транзакцию.
        :param transaction_id: ID транзакции.
        :param path: Путь к файлу с историей транзакций, по умолчанию
         указывает на файл wallets.json в корневой папке.
        :returns: Dict - транзакция или False, если она не существует.
        """
        with open(path, "r") as file:
            data = json.loads(file.read())
            try:
                return next(
                    item
                    for item in data
                    if item["id"] == transaction_id and item["user"] == user
                )
            except StopIteration:
                return False

    @restricted
    def print_history(
            self,
            history: list,
            message: str = Lit.TRANSACTION_HISTORY,
            mode: str = "all",
    ) -> str:
        """
        Вывести историю транзакций пользователя в терминал.

        :param history: История транзакций пользователя.
        :param message: Сообщение, которое будет выведено перед историей,
         по умолчанию равно "История ваших транзакций".
        :param mode: Режим вывода истории, по умолчанию равен "all".
         Всего доступно 3 режима: все транзакции (режим `all`), только
         пополнения (режим `deposit`), и только снятия (режим `withdraw`).
        :returns: Str — сообщение с историей транзакций, либо фраза
         "Ничего не найдено", если подходящие транзакции не были найдены.
        """
        match mode:
            case "all":
                pass
            case "deposit":
                message = Lit.DEPOSIT_HISTORY
                history = (
                    item for item in history if item["category"] == "deposit"
                )
            case "withdraw":
                message = Lit.WITHDRAWAL_HISTORY
                history = (
                    item for item in history if item["category"] == "withdraw"
                )
            case _:
                return Err.UNKNOWN_MODE
        if not history:
            return Err.NOTHING_FOUND
        output_string = f"{message}" + "\n\n".join(
            [
                "\n".join(
                    [
                        f"{TRANSACTION_FIELDS_MAPPING.get(key, key)}: {value}"
                        for key, value in item.items()
                        if key not in "user"
                    ]
                )
                + "\n"
                for item in history
            ]
        ).replace("deposit", "Доход").replace("withdraw", "Расход")
        return output_string

    @restricted
    def get_balance(self, history: list[dict]) -> str:
        """
        Вывести в терминал текущий баланс пользователя.

        :param history: История транзакций пользователя.
        :returns: Str — текущий баланс пользователя.
        """
        deposits = 0
        withdraws = 0
        try:
            for item in history:
                if item["category"] == "deposit":
                    deposits += item["amount"]
                elif item["category"] == "withdraw":
                    withdraws += item["amount"]
            return Lit.CURRENT_BALANCE.format(
                float(deposits - withdraws), float(deposits), float(withdraws)
            )
        except FileNotFoundError:  # для подстраховки на случай первого запуска
            return Lit.CURRENT_BALANCE.format(0.0)

    @staticmethod
    def _write_to_file(
            user: str,
            amount: float,
            category: str,
            description: str,
            encoding: str = "utf-8",
            path: Union[str, Path] = Uc.WALLETS_LOCATION,
    ) -> tuple[dict[str, str | float]]:
        """
        Записать совершенную транзакцию в файл.

        :param user: Пользователь, совершивший транзакцию.
        :param amount: Сумма транзакции.
        :param category: Категория транзакции (доход либо расход).
        :param description: Описание транзакции, указанное пользователем.
        :param encoding: Кодировка файла, по умолчанию равна `utf-8`.
        :param path: Путь к файлу с историей транзакций, по умолчанию
         указывает на файл wallets.json в корневой папке.
        :returns: Словарь с информацией о совершенной транзакции.
        """
        data = []
        json_data = (
            dict(
                id=str(uuid4()),
                user=user,
                date=datetime.now().date().isoformat(),
                category=category,
                amount=amount,
                description=description,
            ),
        )
        try:
            with open(path, "r", encoding=encoding) as file:
                data = json.load(file)
        except FileNotFoundError:
            pass  # для подстраховки на случай первого запуска
        except json.JSONDecodeError:
            pass  # для подстраховки на случай первого запуска
        data.extend(json_data)
        with open(path, "w", encoding=encoding) as file:
            json.dump(data, file, indent=4)
        return json_data

    @restricted
    def search(self, mode: str, user_input: str, history: list[dict]) -> str:
        """
        Поиск по истории транзакций пользователя.

        :param mode: Режим поиска. Доступны следующие варианты:
         `Дата`, `Категория`, `Сумма`, `Описание`.
        :param user_input: Значение для поиска, введённое пользователем.
        :param history: История, в которой следует производить поиск.
        :returns: Str — результат поиска. При отсутствии результатов
         возвращается строка "Ничего не найдено".
        """
        if user_input.isdigit():
            user_input = float(user_input)  # для того чтобы преобразовать
            # значение пользователя в число, подобно тому, как оно хранится
            # в истории.
        results = [res for res in history if res.get(mode) == user_input]
        if results:
            return self.print_history(history=results)
        else:
            return Err.NOTHING_FOUND

    @staticmethod
    def _match_search_mode(mode: str) -> str:
        """
        Вывести подсказку по вариантам поиска в терминале.

        :param mode: Режим поиска.
        :return: Режим поиска.
        """
        match mode:
            case "date":
                print(Lit.DATE_EXAMPLE)
            case "amount":
                print(Lit.AMOUNT_EXAMPLE)
            case "category":
                print(Lit.CATEGORY_EXAMPLE)
            case "description":
                print(Lit.DESCRIPTION_EXAMPLE)
        return mode

    @restricted
    def edit_transaction(
            self,
            transaction_id: str,
            user: str,
            path: Union[str, Path] = Uc.WALLETS_LOCATION,
    ):
        """
        Редактирование существующей транзакции.

        :param transaction_id: UUID идентификатор транзакции.
        :param user: Пользователь, совершивший транзакцию.
        :param path: Путь к файлу с историей транзакций, по умолчанию
         указывает на файл wallets.json в корневой папке.

        :returns: Dict — отредактированная транзакция в случае успеха, либо
         `False`, если произошла ошибка при редактировании.
        """
        with open(path, "r") as file:
            data: list[dict] = json.load(file)
        transaction_to_edit = self._get_transaction_by_id(
            user=user, transaction_id=transaction_id, path=path
        )
        if not transaction_to_edit:
            print(Err.TRANSACTION_NOT_FOUND)
            return False
        newline = "\n"
        print(Lit.TRANSACTION_CURRENT_DATA)
        print(
            f"{newline}".join(
                [
                    f"{TRANSACTION_FIELDS_MAPPING.get(key, key)}: {value}"
                    for key, value in transaction_to_edit.items()
                    if key != "user" and key != "id"
                ]
            )
            .replace("deposit", "Доход")
            .replace("withdraw", "Расход")
        )
        values_to_edit = self._get_values_to_edit(
            fields=list(TRANSACTION_FIELDS_MAPPING.keys()),
        )
        if self._run_edit_checkups(values_to_edit):
            for entry in data:
                for key, value in values_to_edit.items():
                    if (
                            entry["id"] == transaction_id
                            and value
                            and key in transaction_to_edit.keys()
                    ):
                        entry[key] = value
                        print(
                            Lit.TRANSACTION_FIELD_CHANGED.format(
                                TRANSACTION_FIELDS_MAPPING[key], f'"{value}"'
                            )
                        )
            with open(path, "w") as file:
                file.write(json.dumps(data, indent=4))
            print(Lit.TRANSACTION_SUCCESSFULLY_EDITED)
            return True
        else:
            return False

    @staticmethod
    def _run_edit_checkups(transaction_to_edit: dict) -> Union[dict, bool]:
        """
        Проверка корректности данных перед редактированием транзакции.

        :param transaction_to_edit: Данные транзакции для редактирования.
        :returns: Транзакция, если данные корректны, иначе — False.
        """
        if "id" in transaction_to_edit:
            print(Err.ID_CANNOT_BE_CHANGED)
            return False
        if transaction_to_edit["amount"]:
            try:
                transaction_to_edit["amount"] = float(
                    transaction_to_edit["amount"]
                )
            except ValueError:
                print(Err.INVALID_NUMBER)
                return False
        if (
                transaction_to_edit["category"]
                and transaction_to_edit["category"]
                not in DEPOSIT_TYPE_MAPPING.keys()
        ):
            print(Err.INVALID_CATEGORY)
            return False
        if transaction_to_edit["date"] and not re.match(
                r"([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))",
                transaction_to_edit["date"],
        ):
            print(Err.INVALID_DATE)
            return False
        if (
                transaction_to_edit["description"]
                and len(transaction_to_edit["description"])
                > Uc.DESCRIPTION_MAX_LENGTH
        ):
            print(Err.DESCRIPTION_TOO_LONG)
            return False
        return transaction_to_edit

    @staticmethod
    def _get_values_to_edit(
            fields: list[str],
    ) -> dict[str, str | float | None]:
        values_to_edit = {}
        print(Lit.FIELDS_TO_CHANGE_PROMPT)
        for field in fields:
            if field == "date":
                new_value = input(
                    Lit.ENTER_FIELD_VALUE.format(
                        field=TRANSACTION_FIELDS_MAPPING[field],
                        description=Lit.DATE_EXAMPLE,
                    )
                )
            elif field == "category":
                new_value = input(
                    Lit.ENTER_FIELD_VALUE.format(
                        field=TRANSACTION_FIELDS_MAPPING[field],
                        description=Lit.CATEGORY_EXAMPLE,
                    )
                )
            else:
                new_value = input(
                    Lit.ENTER_FIELD_VALUE.format(
                        field=TRANSACTION_FIELDS_MAPPING[field], description=""
                    )
                )
            values_to_edit[field] = new_value
            if field not in TRANSACTION_FIELDS_MAPPING.keys():
                continue
        return values_to_edit

    @staticmethod
    def register(
            user: str,
            password: str,
            path: Union[str, Path] = Uc.USERS_LOCATION,
            encoding: str = "utf-8",
    ) -> str:
        """
        Регистрация нового пользователя.

        :param user: Логин пользователя.
        :param password: Пароль пользователя.
        :param path: Путь к файлу с данными о пользователях, по умолчанию
          указывает на файл users.json в корневой папке.
        :param encoding: Кодировка файла, по умолчанию равна `utf-8`.
        :returns: Str — никнейм зарегистрированного пользователя. В случае,
         если пользователь с таким логином уже существует, то возвращается
          сообщение об ошибке.
        """
        try:
            with open(path, "r") as file:
                users = json.load(file)
                for user_data in users:
                    if user_data["user"] == user:
                        print(Err.USER_ALREADY_EXISTS)
                        return Err.USER_ALREADY_EXISTS
        except FileNotFoundError:
            pass  # подстраховка для первого запуска.
        except json.decoder.JSONDecodeError:
            pass  # аналогично
        data = []
        user_data = dict(
            user=user,
            password=sha256(password.encode()).hexdigest(),
        )
        try:
            with open(path, "r", encoding=encoding) as file:
                data = json.load(file)
        except FileNotFoundError:
            pass  # подстраховка для первого запуска.
        except json.decoder.JSONDecodeError:
            pass  # аналогично
        data.append(user_data)
        with open(path, "w") as file:
            json.dump(data, file, indent=4)
            print(Lit.REGISTRATION_SUCCESSFUL.format(user))
        return user

    def auth(
            self,
            user: str,
            password: str,
            path: Union[str, Path] = Uc.USERS_LOCATION,
    ) -> Union[str, None]:
        """
        Авторизация пользователя по паре логин-пароль.

        :param user: Логин пользователя.
        :param password: Пароль пользователя.
        :param path: Путь к файлу с данными о пользователях, по умолчанию
          указывает на файл users.json в корневой папке.

        :returns: Str — никнейм пользователя, если авторизация прошла успешно.
        """
        user_found = False
        with open(path, "r") as file:
            data = json.loads(file.read())
            for user_data in data:
                if (
                        user_data["user"] == user
                        and user_data["password"]
                        == sha256(password.encode()).hexdigest()
                ):
                    self.user = user
                    self.authenticated = True
                    return user
                else:
                    continue
            if not user_found:
                print(Err.INVALID_CREDENTIALS)
                return Err.INVALID_CREDENTIALS

    @staticmethod
    def get_commands() -> str:
        """
        Вывод списка доступных команд.

        :returns: Str — список команд.
        """
        return Lit.APP_COMMANDS

    def command_resolver(self, command: str) -> Union[bool, None]:
        """
        Маршрутизатор команд. Позволяет либо запрещает пользователю
        использовать те или иные команды, в зависимости от того,
        авторизован пользователь или нет.

        :param command: Str — команда, введённая пользователем.
        :returns: Union[bool, None] — результат выполнения команды.
        """
        if self.authenticated:
            return self._handle_authenticated_commands(command)
        else:
            return self._handle_unauthenticated_commands(command)

    def _handle_authenticated_commands(
            self, command: str
    ) -> Union[bool, None]:
        """
        Маршрутизатор команд для авторизованного пользователя.
        :param command: Str — команда, введённая пользователем.
        :returns: Union[bool, None] — результат выполнения команды.
        """
        match command:
            case "balance":
                return print(self.get_balance(self._get_history(self.user)))
            case "deposit":
                return self.run_transaction(
                    _type="deposit",
                    amount=input(
                        Lit.RUN_TRANSACTION_ENTER_AMOUNT.format(
                            DEPOSIT_TYPE_MAPPING["deposit"]
                        )
                    ),
                    description=input(Lit.TRANSACTION_DESCRIPTION),
                )
            case "withdraw":
                return self.run_transaction(
                    _type="withdraw",
                    amount=input(
                        Lit.RUN_TRANSACTION_ENTER_AMOUNT.format(
                            DEPOSIT_TYPE_MAPPING["withdraw"]
                        )
                    ),
                    description=input(Lit.TRANSACTION_DESCRIPTION),
                )
            case "history":
                print(
                    self.print_history(
                        history=self._get_history(self.user),
                        mode=input(Lit.HISTORY_MODE_CHOICES),
                    )
                )
            case "search":
                mode = input(Lit.SEARCH_MODE_CHOICES)
                self._match_search_mode(mode)
                value = input(Lit.SEARCH_VALUE_INPUT)
                print(self.search(mode, value, self._get_history(self.user)))
            case "edit":
                transaction = input(Lit.ENTER_TRANSACTION_NUMBER)
                return self.edit_transaction(
                    transaction_id=transaction,
                    user=self.user,
                )
            case "help":
                return print(self.get_commands())
            case "exit":
                raise SystemExit
            case _:
                print(Err.INVALID_COMMAND)

    def _handle_unauthenticated_commands(
            self, command: str
    ) -> Union[bool, None, str]:
        """
        Маршрутизатор команд для неавторизованного пользователя.
        :param command: Str — команда, введённая пользователем.
        :returns: Union[bool, None] — результат выполнения команды.
        """
        match command:
            case "register":
                return self.register(
                    user=input(Lit.ENTER_LOGIN_REGISTER),
                    password=mask_input(Lit.ENTER_PASSWORD),
                    path=Uc.USERS_LOCATION,
                )
            case "auth":
                return self.auth(
                    user=input(Lit.ENTER_LOGIN_AUTH),
                    password=mask_input(Lit.ENTER_PASSWORD),
                    path=Uc.USERS_LOCATION,
                )
            case "exit":
                raise SystemExit
            case _:
                print(Err.INVALID_COMMAND)

    def run(self) -> None:
        """
        Точка входа в приложение.
        """
        while True:
            if self.first_time_logged:
                print(Lit.FIRST_TIME_LOGGED_MESSAGE)
                self.first_time_logged = False
            if self.authenticated and self.required_to_show_commands:
                print(Lit.WELCOME_MESSAGE.format(self.user))
                print(self.get_commands())
                self.required_to_show_commands = False
            command = input(Lit.ENTER_COMMAND)
            self.command_resolver(command)


if __name__ == "__main__":
    wallet = Wallet()
    wallet.run()
