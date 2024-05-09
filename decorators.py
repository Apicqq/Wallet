from functools import wraps

from constants import ErrorLiterals as Err


def restricted(func):
    """
    Декоратор для проверки авторизации пользователя в системе.
    :param func: Функция или метод, в котором вызывается проверка.
    :returns: Функция или метод, в котором вызывается проверка, если
     она прошла успешно, либо строка "Вы не вошли в систему", если
     пользователь не авторизован.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not args[0].authenticated:
            return Err.NOT_LOGGED_IN
        return func(*args, **kwargs)

    return wrapper
