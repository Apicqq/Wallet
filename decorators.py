from functools import wraps


def restricted(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not args[0].authenticated:
            return "Вы не вошли в систему"
        return func(*args, **kwargs)

    return wrapper
