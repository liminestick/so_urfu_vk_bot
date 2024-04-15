# VK Quiz Bot

Этот бот для VK позволяет проводить викторины с пользователями. Пользователи могут отвечать на вопросы и получать обратную связь о правильности их ответов.

## Установка

1. Установите необходимые библиотеки:

   ```
   pip install vk_api
   ```
2. Склонируйте репозиторий:
```
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

3. Создайте файл token.txt и поместите в него токен вашего сообщества VK.

4. Запустите бота
```
python main.py
```

## Использование

1. Пользователь может начать викторину, отправив сообщение с текстом "начать викторину".
2. Бот будет поочередно отправлять вопросы, на которые пользователь должен ответить.
3. После ответа на все вопросы пользователь получит итоги викторины.

## Файлы

- main.py - основной файл бота.
- token.txt - файл для хранения токена сообщества VK.
- question.json - файл с вопросами и ответами для викторины.
- HelloMessage.txt - файл с приветственным сообщением.

## Автор

Нигматуллин Айрат ССО «Спарта»
ayrat_n@bk.ru