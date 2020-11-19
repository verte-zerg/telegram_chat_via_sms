import os
import sys
from time import sleep
from datetime import datetime, timezone, timedelta
from typing import List, Set, Dict, Any

import aiotools
import asyncio
from telethon import TelegramClient, events, utils
from telethon.sessions import StringSession
from loguru import logger

from config import Config
from gmail import send_message, recieve_messages


client = TelegramClient(StringSession(Config.SESSION_STRING), Config.API_ID, Config.API_HASH)

last_mail_update = datetime.now()

old_msg_set: Set[str] = set()
new_msg_set: Set[str] = set()


@logger.catch
@client.on(events.NewMessage(**Config.FILTERS))
@client.on(events.MessageEdited(**Config.FILTERS))
async def handler_edit_message(event):
    t = 'N'
    if type(event) == events.MessageEdited.Event:
        t = 'E'
    message = event.message
    chat = await client.get_entity(message.peer_id)
    chat_name = utils.get_display_name(chat)

    user_name = 'me'
    if message.from_id:
        user = await client.get_entity(message.from_id)
        user_name = utils.get_display_name(user)

    logger.info(f'Get new message from user "{user_name}" in chat "{chat_name}"')
    
    tzinfo = timezone(timedelta(hours=Config.TIMEZONE))
    msg_dt = message.date.astimezone(tzinfo)
    subject = f'[{t}: {chat_name}:{user_name}][{msg_dt.strftime("%d.%m %H:%M:%S")}]'
    send_message(message.message, subject)


@logger.catch
def recieve_new_messages() -> List[str]:
    global last_mail_update
    global old_msg_set
    global new_msg_set

    tmp = datetime.now()
    logger.info(f'Get new emails after {last_mail_update}')
    messages = recieve_messages(int(last_mail_update.timestamp()))
    last_mail_update = tmp

    new_msg_set = messages.keys()
    unsend_msg_set = new_msg_set - old_msg_set
    old_msg_set = new_msg_set

    unsend_messages = []
    for msg_id in unsend_msg_set:
        unsend_messages.append(messages[msg_id])

    return unsend_messages


@logger.catch
def get_user_id(msg: str) -> Any:    
    pos_space = msg.find(' ')
    user_name = msg[:pos_space]

    if user_name not in Config.USER_MAP:
        logger.error(f'User with name "{user_name}" not found in USER_MAP')
        return None

    return int(Config.USER_MAP[user_name])


@logger.catch
async def send_telegram_message(user_id: int, msg: str):
    await client.send_message(user_id, msg)


@logger.catch
async def timer_tick(interval):
    for msg in recieve_new_messages():
        user_id = get_user_id(msg)
        msg_wout_user_id = msg

        if user_id:
            pos_space = msg.find(' ')
            msg_wout_user_id = msg[pos_space + 1:]
            logger.info(f'Send telegram message to user_id: {user_id}')
        else:
            user_id = 'me'
            msg_wout_user_id = 'ERROR: INCORRECT USER. MESSAGE:\n' + msg
            logger.info(f'Send telegram message with error to me')

        await send_telegram_message(user_id, msg_wout_user_id)


@logger.catch
async def start_timer():
    await asyncio.sleep(1.0)
    t = aiotools.create_timer(timer_tick, 10.0)
    await t

loop = asyncio.get_event_loop()
loop.create_task(start_timer())

with client:
    client.start()
    client.run_until_disconnected()