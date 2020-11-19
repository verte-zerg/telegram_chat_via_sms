Для работы программы необходимо задать следующие переменные окружения:
API_ID, API_HASH для Telegram, взять с https://my.telegram.org/auth?to=apps.
MAIL_FROM - GMail почта, с которой будет происходить отправка сообщений.
MAIL_TO - почта, на которую будут отправляться, и с которой будет получаться сообщения.
CHATS - ID чатов, которые нужно слушать. Пример: "[111111111, 222222222, 333333333]".
SESSION_STRING - токен для доступа к Telegram аккаунту, получить можно при помощи скрипта get_session_string.py. На момент запуска должны быть заданы переменные API_ID и API_HASH.
USER_MAP - связь между название пользователя, и ID чата. Пример: "user_name_1:user_id_1;user_name_2:user_id_2".