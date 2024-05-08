import json
from uuid import uuid4
from datetime import datetime
from getpass import getpass
from hashlib import sha256
from pathlib import Path
from typing import Union

from constants import (
    UtilityConstants as Uc,
    Literals as Lit,
    ErrorLiterals as Err,
    TRANSACTION_FIELDS_MAPPING,
    DEPOSIT_TYPE_MAPPING,
    EDIT_CATEGORY_MAPPING,
    SEARCH_FIELDS_MAPPING
)
from decorators import restricted


class Wallet:
    def __init__(self):
        self.user = None
        self.authenticated = False
        self.first_time_logged = True

    @restricted
    def run_transaction(
            self,
            _type: str = "deposit",
            path: Union[str, Path] = Uc.WALLETS_LOCATION,
    ) -> bool:
        """
        Провести транзакцию. Возвращает True, если транзакция была
        выполнена, False в противном случае.

        :param _type: Тип транзакции, по умолчанию deposit.
        :param path: Путь к файлу с историей транзакций, по умолчанию
         указывает на файл wallets.json в корневой папке.
        :returns: True если транзакция была выполнена, False в ином случае.
        """
        amount = input(
            Lit.RUN_TRANSACTION_ENTER_AMOUNT.format(
                DEPOSIT_TYPE_MAPPING[_type]
            )
        )
        try:
            amount = float(amount)
        except ValueError:
            print(Err.INVALID_NUMBER)
            return False
        description = input(Lit.TRANSACTION_DESCRIPTION)
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
    def _get_history(user: str, path: str = Uc.WALLETS_LOCATION) -> list[dict]:
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
            user: str, transaction_id: str, path: str = Uc.WALLETS_LOCATION
    ) -> dict:
        with open(path, "r") as file:
            data = json.loads(file.read())
            try:
                return next(
                    item
                    for item in data
                    if item["id"] == transaction_id and item["user"] == user
                )
            except StopIteration:
                return Err.TRANSACTION_NOT_FOUND

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
        # TODO добавить возможность отобразить баланс отдельно доходов,
        # отдельно расходов.
        """
        Вывести в терминал текущий баланс пользователя.

        :param history: История транзакций пользователя.
        :returns: Str — текущий баланс пользователя.
        """
        curr_balance = 0
        try:
            for item in history:
                if item["category"] == "deposit":
                    curr_balance += item["amount"]
                elif item["category"] == "withdraw":
                    curr_balance -= item["amount"]
            return Lit.CURRENT_BALANCE.format(float(curr_balance))
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
    ) -> bool:
        """
        Записать совершенную транзакцию в файл.

        :param user: Пользователь, совершивший транзакцию.
        :param amount: Сумма транзакции.
        :param category: Категория транзакции (доход либо расход).
        :param description: Описание транзакции, указанное пользователем.
        :param encoding: Кодировка файла, по умолчанию равна `utf-8`.
        :param path: Путь к файлу с историей транзакций, по умолчанию
         указывает на файл wallets.json в корневой папке.
        :returns: Bool — True, в случае, если запись в файл прошла успешно.
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
        return True

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
        key = SEARCH_FIELDS_MAPPING.get(mode)
        if user_input.isdigit():
            user_input = float(user_input)  # для того чтобы преобразовать
            # значение пользователя в число, подобно тому, как оно хранится
            # в истории.
        results = [res for res in history if res.get(key) == user_input]
        if results:
            return self.print_history(history=results)
        else:
            return Err.NOTHING_FOUND

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
                transaction_to_edit["category"] and
                transaction_to_edit["category"]
                not in EDIT_CATEGORY_MAPPING.keys()
        ):
            print(Err.INVALID_CATEGORY)
            return False
        return transaction_to_edit

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
            user=user, transaction_id=transaction_id
        )
        if not transaction_to_edit:
            print(Err.TRANSACTION_NOT_FOUND)
            return
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
        print(Lit.FIELDS_TO_CHANGE_PROMPT)
        edited_transaction = dict(
            date=input("Дата: "),
            category=input("Категория. Доступные варианты: Доход, Расход: "),
            amount=input("Сумма: "),
            description=input("Описание: "),
        )
        if self._run_edit_checkups(edited_transaction):
            for entry in data:
                for key, value in edited_transaction.items():
                    if (
                            entry["id"] == transaction_id
                            and value
                            and key in transaction_to_edit.keys()
                    ):
                        if key == "category":
                            value = EDIT_CATEGORY_MAPPING[value]
                        entry[key] = value
                        print(
                            Lit.TRANSACTION_FIELD_CHANGED.format(
                                TRANSACTION_FIELDS_MAPPING[key], f'"{value}"'
                            )
                        )
            with open(path, "w") as file:
                file.write(json.dumps(data, indent=4))
            print(Lit.TRANSACTION_SUCCESSFULLY_EDITED)
            return edited_transaction

    @staticmethod
    def register(path: Union[str, Path], encoding: str = "utf-8") -> str:
        """
        Регистрация нового пользователя.

        :param path: Путь к файлу с данными о пользователях, по умолчанию
          указывает на файл users.json в корневой папке.
        :param encoding: Кодировка файла, по умолчанию равна `utf-8`.
        :returns: Str — никнейм зарегистрированного пользователя. В случае,
         если пользователь с таким логином уже существует, то возвращается
          сообщение об ошибке.
        """
        user = input(Lit.ENTER_LOGIN_REGISTER)
        try:
            with open(path, "r") as file:
                users = json.load(file)
                for user_data in users:
                    if user_data["user"] == user:
                        print(Err.USER_ALREADY_EXISTS)
                        return Err.USER_ALREADY_EXISTS
        except FileNotFoundError:
            pass  # подстраховка для первого запуска.
        password = getpass(prompt=Lit.ENTER_PASSWORD)
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

    def auth(self) -> Union[str, None]:
        """
        Авторизация пользователя по паре логин-пароль.

        :returns: Str — никнейм пользователя, если авторизация прошла успешно.
        """
        user = input(Lit.ENTER_LOGIN_AUTH)
        password = getpass(Lit.ENTER_PASSWORD)
        user_found = False
        with open(Uc.USERS_LOCATION, "r") as file:
            data = json.loads(file.read())
            while not user_found:
                for user_data in data:
                    if (
                            user_data["user"] == user
                            and user_data["password"]
                            == sha256(password.encode()).hexdigest()
                    ):
                        self.user = user
                        self.authenticated = True
                        return user
                print(Err.INVALID_CREDENTIALS)
                user = input(Lit.ENTER_LOGIN_AUTH)
                password = getpass(Lit.ENTER_PASSWORD)
        return

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
                return self.run_transaction(_type="deposit")
            case "withdraw":
                return self.run_transaction(_type="withdraw")
            case "history":
                mode = input(Lit.HISTORY_MODE_CHOICES)
                print(
                    self.print_history(
                        history=self._get_history(self.user), mode=mode
                    )
                )
            case "search":
                mode = input(Lit.SEARCH_MODE_CHOICES)
                value = input(Lit.SEARCH_VALUE_INPUT)
                return print(
                    self.search(mode, value, self._get_history(self.user))
                )
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
                return self.register(path=Uc.USERS_LOCATION)
            case "auth":
                return self.auth()
            case "exit":
                raise SystemExit
            case _:
                print(Err.INVALID_COMMAND)

    def run(self) -> None:
        """
        Точка входа в приложение.
        """
        while True:
            if not self.authenticated:
                print(Lit.FIRST_TIME_LOGGED_MESSAGE)
            else:
                if self.first_time_logged:
                    print(Lit.WELCOME_MESSAGE.format(self.user))
                    print(self.get_commands())
                    self.first_time_logged = False
            command = input(Lit.ENTER_COMMAND)
            self.command_resolver(command)


if __name__ == "__main__":
    wallet = Wallet()
    wallet.run()
