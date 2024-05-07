# Личный финансовый кошелек

Приложение, помогающие вам вести учёт своих трат, и более осознанно подходить к ведению личного бюджета (а возможно и семьи!).

## Ключевые возможности приложения
- Добавление новой записи о доходе или расходе в ваш личный кошелёк.
- Отображение баланса как в целом, так и по отдельности (доходов и расходов).
- Поиск по записям: Поиск записей по категории, дате или сумме.
- Редактирование записи: Изменение существующих записей о доходах и расходах.
- Регистрация/Авторизация: никто не сможет подсмотреть список ваших трат! Доступ к данным доступен только после авторизации в приложении.

## Использованные технологии
- Python 3.10
- pytest

## Как установить и запустить проект

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Apicqq/Wallet
```

```
cd wallet
```

Создать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Запустить проект:
```
python main.py
```

