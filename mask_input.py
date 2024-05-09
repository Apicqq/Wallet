from msvcrt import getwch


def mask_input(prompt='', mask='*'):
    """
    Прячет ввод пароля, заменяя символы на звездочки.

    :param prompt: Подсказка для ввода.
    :param mask: Символ для замены.
    :return: Введённая пользователем строка.
    """
    print(prompt, end='', flush=True)
    response = ''
    while (char := getwch()) != '\r':
        if char == '\x08':  # backspace
            print('\b \b', end='', flush=True)
            response = response[:-1]
        else:
            response += char
            print(mask, end='', flush=True)
    print("")
    return response
