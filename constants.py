from pathlib import Path

TRANSACTION_FIELDS_MAPPING = {
    "date": "Дата",
    "category": "Категория",
    "amount": "Сумма",
    "description": "Описание",
}
DEPOSIT_TYPE_MAPPING = {
    "deposit": "внесения",
    "withdraw": "снятия",
}


class UtilityConstants:
    BASE_DIR = Path(__file__).parent
    WALLETS_LOCATION = BASE_DIR / "wallets.json"
    USERS_LOCATION = BASE_DIR / "users.json"
    DESCRIPTION_MAX_LENGTH = 100


class Literals:
    RUN_TRANSACTION_ENTER_AMOUNT = "Введите сумму для {}: "
    ENTER_TRANSACTION_NUMBER = "Введите ID транзакции: "
    SEARCH_VALUE_INPUT = "Введите значение для поиска: "
    TRANSACTION_DESCRIPTION = "Введите описание для транзакции: "
    TRANSACTION_ACCEPTED = "Данные внесены. "
    TRANSACTION_HISTORY = "\nИстория ваших транзакций:\n\n"
    DEPOSIT_HISTORY = "\nИстория ваших пополнений:\n\n"
    WITHDRAWAL_HISTORY = "\nИстория ваших снятий:\n\n"
    CURRENT_BALANCE = "Ваш текущий баланс: {}\n\nДоходы: {}, Расходы: {}"
    TRANSACTION_CURRENT_DATA = "Текущие данные по транзакции: \n"
    FIELDS_TO_CHANGE_PROMPT = (
        "Какие поля вы хотите изменить? Пожалуйста, введите значение для поля,"
        " если хотите изменить его, либо нажмите Enter,"
        " чтобы оставить поле без изменения."
    )
    TRANSACTION_FIELD_CHANGED = "Поле {} изменено на {}"
    TRANSACTION_SUCCESSFULLY_EDITED = "Транзакция успешно отредактирована."
    ENTER_LOGIN_REGISTER = "Введите логин для регистрации: "
    ENTER_LOGIN_AUTH = "Введите логин для входа: "
    ENTER_PASSWORD = "Введите пароль: "
    REGISTRATION_SUCCESSFUL = "Вы успешно зарегистрировались, {}!\n"
    APP_COMMANDS = (
        "Список команд: "
        "\n- balance — проверить баланс"
        "\n- deposit — внести данные о доходах"
        "\n- withdraw — внести данные о расходах"
        "\n- history — посмотреть историю транзакций"
        "\n- search — поиск по вашим транзакциям"
        "\n- edit — изменить данные транзакции по её ID. Его можно найти в "
        "истории ваших транзакций."
        "\n- help - вывести список доступных команд"
        "\n- exit — выход из приложения"
    )
    HISTORY_MODE_CHOICES = (
        "Укажите, какие транзакции вы хотите посмотреть: \n"
        "- all - все\n"
        "- deposit - только пополнения\n"
        "- withdraw - только снятия\n"
    )
    SEARCH_MODE_CHOICES = (
        "Выберите критерий поиска:"
        "\n- date — Дата"
        "\n- category — Категория"
        "\n- amount — Сумма"
        "\n- description — Описание\n"
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
    ENTER_FIELD_VALUE = "Введите значение для поля {field}. {description}\n"
    DATE_EXAMPLE = "Пример даты: 2020-12-31"
    AMOUNT_EXAMPLE = "Пример суммы: 100"
    CATEGORY_EXAMPLE = (
        "Доступные категории — deposit или withdraw (Доход или Расход)"
    )
    DESCRIPTION_EXAMPLE = "Пример описания: Куплен новый ноутбук"


class ErrorLiterals:
    INVALID_CREDENTIALS = "Неверные имя пользователя или пароль"
    INVALID_COMMAND = "Неверная либо несуществующая команда"
    USER_ALREADY_EXISTS = (
        "Такой пользователь уже существует, "
        "пожалуйста, попробуйте ещё раз."
    )
    INVALID_NUMBER = "Ошибка: сумма должна быть числом.\n"
    INVALID_CATEGORY = "Ошибка: Недопустимая категория.\n"
    INVALID_DATE = "Ошибка: Недопустимый формат даты.\n"
    DESCRIPTION_TOO_LONG = "Ошибка: Описание слишком длинное.\n"
    UNKNOWN_MODE = "Неизвестный режим"
    NOTHING_FOUND = "Ничего не найдено"
    ID_CANNOT_BE_CHANGED = "Ошибка: id транзакции не может быть изменён"
    TRANSACTION_NOT_FOUND = "Транзакция с указанным id не найдена"
    NOT_LOGGED_IN = "Вы не вошли в систему"
