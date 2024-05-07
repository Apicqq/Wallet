import json
from datetime import datetime
from getpass import getpass
from hashlib import sha256
from typing import Union, Generator

from constants import UtilityConstants as Uc
from decorators import restricted


class Wallet:
    def __init__(self):
        self.user = None
        self.authenticated = False
        self.first_time_logged = True

    @restricted
    # TODO write tests
    def run_transaction(
            self,
            _type: str = "deposit",
    ) -> bool:
        KEYS = {
            "deposit": "внесения",
            "withdraw": "снятия",
        }
        amount = input(f"Введите сумму для {KEYS[_type]}: ")
        try:
            amount = float(amount)
        except ValueError:
            print("Ошибка: сумма должна быть числом.\n")
            return False
        description = input(f"Введите описание для транзакции: ")
        if _type == "deposit":
            self._write_to_file(
                self.user, amount, category="deposit", description=description
            )
        elif _type == "withdraw":
            self._write_to_file(
                self.user, amount, category="withdraw", description=description
            )
        print(f"Сумма внесена на счёт. {self.get_balance(self.user)}")

    @staticmethod
    def _get_history(user: str) -> Generator[dict, None, None]:
        with open(Uc.WALLETS_LOCATION, "r") as file:
            data = json.loads(file.read())
            return (item for item in data if item["user"] == user)

    @restricted
    def print_history(
            self,
            message: str = "\nИстория ваших транзакций:\n\n",
            mode: str = "all",
    ) -> Union[str, None]:
        history = self._get_history(self.user)
        KEYS = {
            "date": "Дата",
            "category": "Категория",
            "amount": "Сумма",
            "description": "Описание",
        }
        match mode:
            case "all":
                pass
            case "deposit":
                message = "\nИстория ваших пополнений:\n\n"
                history = (
                    item for item in history if item["category"] == "deposit"
                )
            case "withdraw":
                message = "\nИстория ваших снятий:\n\n"
                history = (
                    item for item in history if item["category"] == "withdraw"
                )
            case _:
                return "Неизвестный режим"
        if not history:
            return "Ничего не найдено"
        output_string = f"{message}" + "\n\n".join(
            [
                "\n".join(
                    [
                        f"{KEYS.get(key, key)}: {value}"
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
    def get_balance(self, user: str) -> str:
        curr_balance = 0
        try:
            for item in self._get_history(user):
                if item["category"] == "deposit":
                    curr_balance += item["amount"]
                elif item["category"] == "withdraw":
                    curr_balance -= item["amount"]
            return f"Ваш текущий баланс: {float(curr_balance)}"
        except FileNotFoundError:
            return "Ваш текущий баланс: 0.0"

    @staticmethod
    def _write_to_file(
            user: str,
            amount: float,
            category: str,
            description: str,
            encoding: str = "utf-8",
    ) -> None:
        data = []
        json_data = (
            dict(
                user=user,
                date=datetime.now().date().isoformat(),
                category=category,
                amount=amount,
                description=description,
            ),
        )
        try:
            with open(Uc.WALLETS_LOCATION, "r", encoding=encoding) as file:
                data = json.load(file)
        except FileNotFoundError:
            pass
        data.extend(json_data)
        with open(Uc.WALLETS_LOCATION, "w", encoding=encoding) as file:
            json.dump(data, file, indent=4)

    @restricted
    def search(
            self,
            mode: str,
            user_input: str,
    ) -> str:
        history = self._get_history(self.user)
        key_map = {
            "Дата": "date",
            "Категория": "category",
            "Сумма": "amount",
            "Описание": "description",
        }
        key = key_map.get(mode)
        if user_input.isdigit():
            user_input = float(user_input)  # to match values from the history
        results = (res for res in history if res.get(key) == user_input)
        if results:
            return self.print_history()
        else:
            return "Ничего не найдено"

    @restricted
    def edit_transaction(self):
        with open(f"{Uc.WALLETS_DIR}/{self.user}_wallet.json", "r") as file:
            pass

    def register(self, encoding: str = "utf-8") -> str:
        user = input("Введите логин для регистрации: ")
        try:
            with open(Uc.USERS_LOCATION, "r") as file:
                users = json.load(file)
                for user_data in users:
                    if user_data["user"] == user:
                        print(
                            "Такой пользователь уже существует,"
                            "пожалуйста, попробуйте ещё раз."
                        )
                        return self.register(encoding=encoding)
        except FileNotFoundError:
            pass
        password = getpass(prompt="Введите пароль: ")
        data = []
        user_data = dict(
            user=user,
            password=sha256(password.encode()).hexdigest(),
        )
        try:
            with open(Uc.USERS_LOCATION, "r", encoding=encoding) as file:
                data = json.load(file)
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            pass
        data.append(user_data)
        with open(Uc.USERS_LOCATION, "w") as file:
            json.dump(data, file, indent=4)
            print(f"Вы успешно зарегистрировались, {user}!\n")
        return user

    def auth(self) -> Union[str, None]:
        user = input("Введите логин для входа: ")
        password = getpass("Введите пароль: ")
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
                print("Неправильный логин или пароль")
                user = input("Введите логин для входа: ")
                password = getpass("Введите пароль: ")
        return

    @staticmethod
    def get_commands() -> str:
        return (
            "Список команд: "
            "\n1. balance — проверить баланс"
            "\n2. deposit — внести средства"
            "\n3. withdraw — снять средства"
            "\n4. history — посмотреть историю"
            "\n5. search — поиск по вашим транзакциям"
            "\n6. help - вывести список доступных команд"
            "\n6. exit — выход из приложения"
        )

    def command_resolver(self, command: str) -> Union[bool, None]:
        if self.authenticated:
            return self._handle_authenticated_commands(command)
        else:
            return self._handle_unauthenticated_commands(command)

    def _handle_authenticated_commands(
            self, command: str
    ) -> Union[bool, None]:
        match command:
            case "balance":
                return print(self.get_balance(self.user))
            case "deposit":
                return self.run_transaction(_type="deposit")
            case "withdraw":
                return self.run_transaction(_type="withdraw")
            case "history":
                mode = input(
                    "Укажите, какие транзакции вы хотите посмотреть: \n"
                    "1. all - все\n"
                    "2. deposit - только пополнения\n"
                    "3. withdraw - только снятия\n"
                )
                print(self.print_history(mode=mode))
            case "search":
                mode = input(
                    "Выберите критерий поиска: \n1. Дата\n2. Категория\n"
                    "3. Сумма\n4. Описание\n"
                )
                value = input("Введите значение: ")
                return print(self.search(mode, value))
            case "help":
                return print(self.get_commands())
            case "exit":
                raise SystemExit
            case _:
                print("Неверная либо несуществующая команда")

    def _handle_unauthenticated_commands(self, command: str) -> Union[
        bool, None, str
    ]:
        match command:
            case "register":
                return self.register()
            case "auth":
                return self.auth()
            case "exit":
                raise SystemExit
            case _:
                print("Неверная либо несуществующая команда")

    def run(self) -> None:
        while True:
            if not self.authenticated:
                print(
                    "Здравствуйте! Для того, чтобы воспользоваться кошельком,"
                    "нужно войти в систему, либо,"
                    " если вы ещё не зарегистрированы, — зарегистрироваться."
                    " Введите команду register для регистрации, либо auth,"
                    " чтобы войти в свой аккаунт. \n\n"
                    "Для выхода из приложения введите команду exit либо "
                    "нажмите комбинацию клавиш Ctrl+C. \n"
                )
            else:
                if self.first_time_logged:
                    print(f"Добро пожаловать, {self.user}!\n")
                    print(self.get_commands())
                    self.first_time_logged = False
            command = input("Введите команду: ")
            self.command_resolver(command)


if __name__ == "__main__":
    wallet = Wallet()
    wallet.run()
