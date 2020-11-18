import os
from datetime import datetime, timezone, timedelta

from telethon import TelegramClient, events, utils
from telethon.sessions import StringSession

from config import Config
from gmail import send_message


client = TelegramClient(StringSession(Config.SESSION_STRING), Config.API_ID, Config.API_HASH)


@client.on(events.NewMessage(**Config.FILTERS))
@client.on(events.MessageEdited(**Config.FILTERS))
async def handler_edit_message(event):
    print(event)
    t = 'N'
    if type(event) == events.MessageEdited.Event:
        t = 'E'
    message = event.message
    
    chat = await client.get_entity(message.peer_id)
    chat_name = utils.get_display_name(chat)

    user = await client.get_entity(message.from_id)
    user_name = utils.get_display_name(user)

    tzinfo = timezone(timedelta(hours=Config.TIMEZONE))
    msg_dt = message.date.astimezone(tzinfo)
    subject = f'[{t}: {chat_name}:{user_name}][{msg_dt.strftime("%d.%m %H:%M:%S")}]'
    print(subject)
    print(message.message)
    send_message(message.message, subject)


def get_dialogs_id(client):
    for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)


with client:
    client.start()
    client.run_until_disconnected()