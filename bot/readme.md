# Neural Teachers Bot

Бот, являющийся частью проекта "Neural Teachers", идея которого состоит в генерации цитат преподавателей ВУЗов и школ с помощью нейросети.

## Возможности

* Генерация цитат преподавателей, используя предобученную модель. Поддерживается два типа генерации: случайные цитаты (по команде `/рандом`), а также продолжение пользовательского ввода: пользователь вводит любой текст, а модель его продолжает, генерируя цитату.
* Возможность оценить сгенерированные цитаты.
* Автопостинг понравившихся пользователям цитат на стену.

## Зависимости

Бот написан с использованием асинхронного фреймворка `VKBottle`. Для асинхронной работы с базой данной используется библиотека `Aiosqlite`, а для запросов к API с моделью - `AIOHTTP`. Кроме того, используется модуль `Scheduler`, который отвечает за автопостинг на стену каждые полчаса.

Установить все зависимости очень просто: `pip3 install -r requirements.txt`.

## Настройка ВКонтакте

Первый этап - необходимо включить сообщения вашего сообщества, возможности ботов, а также API, в частности, LongPoll API. Далее необходимо сгенерировать токен доступа. Полученный ключ сохраните в переменную `VK_TOKEN` в `config.py`.

К сожалению, VK сделали очень странную штуку: нет возможности добавлять пост на стену с ключём доступа сообщества, придётся получить тот, который будет ассоциирован с пользователем-владельцем. Самый простой вариант, перейти [сюда](https://vkhost.github.io), выбрать "VK Admin" / "VK Admin для iOS", предоставить разрешение и скопировать токен (это безопасно, но неофициально). Более законный вариант - создать своё standalone-приложение и получить доступ к пользователю через него. Так или иначе, ассоциированный с администратором группы токен нужно положить в `VK_SERVICE_TOKEN`.

Для автопостинга на стену в переменную `GROUP_ID` необходимо записать ID сообщества, в котором будет работать бот (**со знаком минуса (-)**).

Наконец, надо получить токен 🤗 для работы с моделью и записать его в `HF_TOKEN`.

По желанию можно поменять модель на большую, убрав суффикс `_small` в `HF_MODEL`.

## Запуск

Всё просто: `python3 bot.py`.

Если на предыдущем шаге всё сделано верно, бот запустится, а в терминале появятся логи. Они также будут дублироваться в `bot.log`.

## Использование

Напишите `/рандом`, чтобы получить несколько сгенерированных цитат.

Напишите любой текст, чтобы продолжить его с помощью модели.

Оценивайте цитаты с помощью кнопок под каждым сообщением. Понравившиеся попадут на стену, непонравившиеся - далеко-далеко, в специальную табличку в базе данных.

Каждый час заходите на стену группы и радуйтесь новому гениальному шедевру.
