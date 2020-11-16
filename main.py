import os
import smtplib
from typing import Dict, NamedTuple
from datetime import datetime

from telethon import TelegramClient, events, utils

from config import Config
from gmail import send_message


Message = NamedTuple('Message', [('user', str), ('dt', datetime), ('text', str)])

api_id = Config.API_ID
api_hash = Config.API_HASH

client = TelegramClient('anon', api_id, api_hash)

messages: Dict[int, Message] = {}

@client.on(events.NewMessage(**Config.FILTERS))
async def handler_new_message(event):
    message = event.message
    user = await client.get_entity(message.peer_id)
    username = utils.get_display_name(user)
    messages[message.id] = Message(user=username, dt=datetime.now(), text=message.message)
    res = []
    res.append(f'[NEW MESSAGE FROM USER {username}][{datetime.now()}]')
    res.append(message.message)
    print('\n'.join(res))
    send_message('\n'.join(res))


@client.on(events.MessageEdited(**Config.FILTERS))
async def handler_edit_message(event):
    message = event.message
    user = await client.get_entity(message.peer_id)
    username = utils.get_display_name(user)
    res = []
    res.append(f'[EDIT MESSAGE FROM USER {username}][{datetime.now()}]')
    if message.id in messages:
        res.append('[OLD_MESSAGE]\n' + messages[message.id].text)
    else:
        res.append('[OLD_MESSAGE_NOT_SAVED]')

    messages[message.id] = Message(user=username, dt=datetime.now(), text=message.message)
    res.append('[NEW_MESSAGE]\n' + messages[message.id].text)
    print('\n'.join(res))
    send_message('\n'.join(res))


@client.on(events.MessageDeleted(**Config.FILTERS))
async def handler_delete_message(event):
    first_id = event.deleted_ids[-1]
    if first_id in messages:
        username = messages[first_id].user
    else:
        username = 'UNKNOWN'
    res = []
    res.append(f'[DELETED MESSAGES FROM USER {username}][{datetime.now()}]')
    for message_id in event.deleted_ids:
        if message_id in messages:
            res.append(f'[{messages[message_id].dt}] {messages[message_id].text}')
        else:
            res.append(f'MESSAGE WITH ID={message_id} NOT FOUND')
    print('\n'.join(res))
    send_message('\n'.join(res))


def get_dialogs_id(client):
    for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)


with client:
    client.start()
    client.run_until_disconnected()