import json
import uuid
from datetime import datetime
from getpass import getpass
from hashlib import sha256
from pathlib import Path
from typing import Union

from constants import UtilityConstants as Uc
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
            f"Сумма внесена на счёт. "
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

    @restricted
    def print_history(
        self,
        history: list,
        message: str = "\nИстория ваших транзакций:\n\n",
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
            return f"Ваш текущий баланс: {float(curr_balance)}"
        except FileNotFoundError:  # для подстраховки на случай первого запуска
            return "Ваш текущий баланс: 0.0"

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
                id=str(uuid.uuid4()),
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
        key_map = {
            "Дата": "date",
            "Категория": "category",
            "Сумма": "amount",
            "Описание": "description",
        }
        key = key_map.get(mode)
        if user_input.isdigit():
            user_input = float(user_input)  # для того чтобы преобразовать
            # значение пользователя в число, подобно тому, как оно хранится
            # в истории.
        results = [res for res in history if res.get(key) == user_input]
        if results:
            return self.print_history(history=results)
        else:
            return "Ничего не найдено"

    @restricted
    def edit_transaction(self):
        """
        Редактирование существующей транзакции.
        #TODO написать этот метод.
        :return:
        """
        with open(f"{Uc.WALLETS_DIR}/{self.user}_wallet.json", "r") as file:
            pass

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
        user_already_exists = (
            "Такой пользователь уже существует,"
            "пожалуйста, попробуйте ещё раз."
        )
        user = input("Введите логин для регистрации: ")
        try:
            with open(path, "r") as file:
                users = json.load(file)
                for user_data in users:
                    if user_data["user"] == user:
                        print(user_already_exists)
                        return user_already_exists
        except FileNotFoundError:
            pass  # подстраховка для первого запуска.
        password = getpass(prompt="Введите пароль: ")
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
            print(f"Вы успешно зарегистрировались, {user}!\n")
        return user

    def auth(self) -> Union[str, None]:
        """
        Авторизация пользователя по паре логин-пароль.

        :returns: Str — никнейм пользователя, если авторизация прошла успешно.
        """
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
        """
        Вывод списка доступных команд.

        :returns: Str — список команд.
        """
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
                mode = input(
                    "Укажите, какие транзакции вы хотите посмотреть: \n"
                    "1. all - все\n"
                    "2. deposit - только пополнения\n"
                    "3. withdraw - только снятия\n"
                )
                print(
                    self.print_history(
                        history=self._get_history(self.user), mode=mode
                    )
                )
            case "search":
                mode = input(
                    "Выберите критерий поиска: \n1. Дата\n2. Категория\n"
                    "3. Сумма\n4. Описание\n"
                )
                value = input("Введите значение: ")
                return print(
                    self.search(mode, value, self._get_history(self.user))
                )
            case "edit":
                return self.edit_transaction()
            case "help":
                return print(self.get_commands())
            case "exit":
                raise SystemExit
            case _:
                print("Неверная либо несуществующая команда")

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
                print("Неверная либо несуществующая команда")

    def run(self) -> None:
        """
        Точка входа в приложение.
        """
        while True:
            if not self.authenticated:
                print(
                    "Здравствуйте! Для того, чтобы воспользоваться кошельком,"
                    " нужно войти в систему, либо,"
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
