from pathlib import Path

TRANSACTION_FIELDS_MAPPING = {
    "date": "Дата",
    "category": "Категория",
    "amount": "Сумма",
    "description": "Описание",
}
SEARCH_FIELDS_MAPPING = {
    "Дата": "date",
    "Категория": "category",
    "Сумма": "amount",
    "Описание": "description",
}
DEPOSIT_TYPE_MAPPING = {
    "deposit": "внесения",
    "withdraw": "снятия",
}
EDIT_CATEGORY_MAPPING = {
    "Доход": "deposit",
    "Расход": "withdraw",
}


class UtilityConstants:
    BASE_DIR = Path(__file__).parent
    WALLETS_LOCATION = BASE_DIR / "wallets.json"
    USERS_LOCATION = BASE_DIR / "users.json"


class Literals:
    RUN_TRANSACTION_ENTER_AMOUNT = "Введите сумму для {}"
    ENTER_TRANSACTION_NUMBER = "Введите номер транзакции: "
    SEARCH_VALUE_INPUT = "Введите значение для поиска: "
    TRANSACTION_DESCRIPTION = "Введите описание для транзакции: "
    TRANSACTION_ACCEPTED = "Сумма внесена на счёт. "
    TRANSACTION_HISTORY = "\nИстория ваших транзакций:\n\n"
    DEPOSIT_HISTORY = "\nИстория ваших пополнений:\n\n"
    WITHDRAWAL_HISTORY = "\nИстория ваших снятий:\n\n"
    CURRENT_BALANCE = "Ваш текущий баланс: {}"
    TRANSACTION_CURRENT_DATA = "Текущие данные по транзакции: \n"
    FIELDS_TO_CHANGE_PROMPT = (
        "Какие поля вы хотите изменить? Пожалуйста, введите значение для поля,"
        " если хотите изменить его, либо нажмите Enter,"
        " чтобы оставить поле без изменения."
    )
    TRANSACTION_FIELD_CHANGED = "Поле {} изменено на {}"
    TRANSACTION_SUCCESSFULLY_EDITED = "Транзакция успешно отредактирована"
    ENTER_LOGIN_REGISTER = "Введите логин для регистрации: "
    ENTER_LOGIN_AUTH = "Введите логин для входа: "
    ENTER_PASSWORD = "Введите пароль: "
    REGISTRATION_SUCCESSFUL = "Вы успешно зарегистрировались, {}!\n"
    APP_COMMANDS = (
        "Список команд: "
        "\n1. balance — проверить баланс"
        "\n2. deposit — внести средства"
        "\n3. withdraw — снять средства"
        "\n4. history — посмотреть историю"
        "\n5. search — поиск по вашим транзакциям"
        "\n6. edit — изменить данные по транзакции"
        "\n7. help - вывести список доступных команд"
        "\n8. exit — выход из приложения"
    )
    HISTORY_MODE_CHOICES = (
        "Укажите, какие транзакции вы хотите посмотреть: \n"
        "1. all - все\n"
        "2. deposit - только пополнения\n"
        "3. withdraw - только снятия\n"
    )
    SEARCH_MODE_CHOICES = (
        "Выберите критерий поиска: \n1. Дата\n2. Категория\n"
        "3. Сумма\n4. Описание\n"
    )
    FIRST_TIME_LOGGED_MESSAGE = (
        "Здравствуйте! Для того, чтобы воспользоваться кошельком,"
        " нужно войти в систему, либо,"
        " если вы ещё не зарегистрированы, — зарегистрироваться."
        " Введите команду register для регистрации, либо auth,"
        " чтобы войти в свой аккаунт. \n\n"
        "Для выхода из приложения введите команду exit либо "
        "нажмите комбинацию клавиш Ctrl+C. \n"
    )
    WELCOME_MESSAGE = "Добро пожаловать, {}!\n"
    ENTER_COMMAND = "Введите команду: "


class ErrorLiterals:
    INVALID_CREDENTIALS = "Неверные имя пользователя или пароль"
    INVALID_COMMAND = "Неверная либо несуществующая команда"
    USER_ALREADY_EXISTS = (
        "Такой пользователь уже существует,"
        "пожалуйста, попробуйте ещё раз."
    )
    INVALID_NUMBER = "Ошибка: сумма должна быть числом.\n"
    INVALID_CATEGORY = "Ошибка: Недопустимая категория.\n"
    UNKNOWN_MODE = "Неизвестный режим"
    NOTHING_FOUND = "Ничего не найдено"
    ID_CANNOT_BE_CHANGED = "Ошибка: id транзакции не может быть изменён"
    TRANSACTION_NOT_FOUND = "Транзакция с указанным id не найдена"
