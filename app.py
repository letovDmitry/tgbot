import asyncio
import pymongo
from dotenv import dotenv_values
from opentele.tl import TelegramClient
from telethon import TelegramClient, events
from telethon.tl.custom.button import Button

from functions.get_chats_from_db import get_chats_from_db
from functions.add_accounts_from_tdata import add_accounts_from_tdata
from functions.add_chat_to_db import add_chat_to_db
from functions.add_user import add_user

accounts = []
db_client = pymongo.MongoClient("mongodb://localhost:27017")
current_db = db_client['bot']
chats = current_db['chats']
message = ['привет']

async def main():
    # Connecting accounts
    config = dotenv_values(".env")

    api_id = config['API_ID']
    api_hash = config['API_HASH']
    phone = config['PHONE']
    BOT_TOKEN = config['BOT_TOKEN']


    client = TelegramClient(phone, api_id, api_hash)

    bot_client = await TelegramClient('bot', api_id, api_hash).start(bot_token=BOT_TOKEN)

    await client.connect()

    accounts.append(client)

    async def connect_all_accounts():
        print(accounts)
        for account in accounts:
            await account.connect()

    await connect_all_accounts()

    # Commands

    @bot_client.on(events.NewMessage(pattern='/(?i)start'))
    async def handler(event):
        print('start')
        sender = await event.get_sender()
        SENDER = sender
        await bot_client.send_message(SENDER, 'Команды:', buttons=[
            [Button.text("/база", resize=True),
             Button.text("/добавить_группу", resize=True), ],
            [Button.text("/удалить_группу", resize=True),
             Button.text("/сообщение", resize=True), ],
            [Button.text("/установить_сообщение", resize=True),
             Button.text("/начать_рассылку", resize=True), ],
            [Button.text("/добавить_аккаунты", resize=True),
             Button.text("/начать_инвайтинг", resize=True), ],
            [Button.text("/количество_аккаунтов", resize=True), ]
        ])

    @bot_client.on(events.NewMessage(pattern='/(?i)добавить_аккаунты'))
    async def handler(event):
        print('add accounts')
        sender = await event.get_sender()
        SENDER = sender
        async with bot_client.conversation(SENDER) as conv:
            await conv.send_message('Отправьте архив с аккаунтами в виде tdata')
            msg = await conv.get_response()
            file = await bot_client.download_media(msg.media)
            print(file)
            await add_accounts_from_tdata(file, accounts=accounts)

            await connect_all_accounts()
            await conv.send_message("Успешно")

    @bot_client.on(events.NewMessage(pattern='/(?i)количество_аккаунтов'))
    async def handler(event):
        print('list_accounts')
        sender = await event.get_sender()
        SENDER = sender
        await bot_client.send_message(SENDER, "Количество аккаунтов: " + str(len(accounts)))

    @bot_client.on(events.NewMessage(pattern='/(?i)база'))
    async def handler(event):
        sender = await event.get_sender()
        SENDER = sender
        await bot_client.send_message(SENDER, get_chats_from_db(chats=chats))

    @bot_client.on(events.NewMessage(pattern='/(?i)сообщение'))
    async def handler(event):
        print('message')
        sender = await event.get_sender()
        SENDER = sender.id
        if isinstance(message[0], list):
            await bot_client.send_message(SENDER, message[0][0], file=message[0][1])
        else:
            await bot_client.send_message(SENDER, message[0])
            print(message[0])

    @bot_client.on(events.NewMessage(pattern='/(?i)установить_сообщение'))
    async def handler(event):
        print('set message')
        sender = await event.get_sender()
        SENDER = sender.id
        async with bot_client.conversation(SENDER) as conv:
            await conv.send_message('Введите сообщение для рассылки')
            msg = await conv.get_response()
            if msg.media:
                file = await bot_client.download_media(msg.media, './')
                message.append([msg.message, file])
                message.pop(0)

            else:
                message.append(msg.message)
                message.pop(0)
            print(message)

        await bot_client.send_message(SENDER, 'Успешно')

    @bot_client.on(events.NewMessage(pattern='/(?i)начать_рассылку'))
    async def handler(event):
        print('start messaging')
        sender = await event.get_sender()
        SENDER = sender.id
        arr1 = []
        async with bot_client.conversation(SENDER) as conv:
            await conv.send_message('Введите количество человек')
            number = await conv.get_response()
            await conv.send_message('Начинаю рассылку.......')

            for i in chats.find():
                arr1.extend(i["users"])

            for i in arr1:
                if not i:
                    arr1.remove(i)

            print(number.message)

            arr2 = arr1[1:int(number.message)]
            print(arr2)

            l = len(accounts)

            for account in accounts:
                for i in arr2[:l]:
                    await account.connect()
                    if isinstance(i, str):
                        if isinstance(message[0], list):
                            await account.send_message(i, message[0][0], file=message[0][1])
                        else:
                            await account.send_message(i, message[0])
                    arr2.remove(i)

            await bot_client.send_message(SENDER, 'Успешно разослано ' + number.message + ' сообщений')

    @bot_client.on(events.NewMessage(pattern='/(?i)добавить_группу'))
    async def handler(event):
        print('add group')
        sender = await event.get_sender()
        SENDER = sender.id

        async with bot_client.conversation(SENDER) as conv:
            await conv.send_message('Введите ссылку на группу')
            group = await conv.get_response()
            await conv.send_message('Начинаю парсинг........')
            print(group.message)
            try:
                await add_chat_to_db(group.message, chats=chats, accounts=accounts)
                await conv.send_message('Успешно')
            except:
                await conv.send_message('Бот уже состоит в группе')

    @bot_client.on(events.NewMessage(pattern='/(?i)удалить_группу'))
    async def handler(event):
        print('delete group')
        sender = await event.get_sender()
        SENDER = sender.id

        async with bot_client.conversation(SENDER) as conv:
            await conv.send_message('Введите название группы')
            group = await conv.get_response()
            await bot_client.send_message(SENDER, 'Начинаю удаление.....')

            chats.delete_one({'name': group.message})

            await bot_client.send_message(SENDER, 'Успешно')

    @bot_client.on(events.NewMessage(pattern='/(?i)начать_инвайтинг'))
    async def handler(event):
        print("start inviting")
        sender = await event.get_sender()
        SENDER = sender.id
        arr1 = []
        async with bot_client.conversation(SENDER) as conv:
            await conv.send_message('Введите количество человек')
            number = await conv.get_response()
            await conv.send_message('Введите ссылку на чат для инвайтинга')
            invite_chat = await conv.get_response()
            await conv.send_message('Начинаю инвайтинг.......')

            for i in chats.find():
                arr1.extend(i["users"])

            for i in arr1:
                if not i:
                    arr1.remove(i)

            print(number.message)

            arr2 = arr1[1:int(number.message)]
            print(arr2)

            l = len(accounts)

            invited_count = 0
            for account in accounts:
                for i in arr2[:l]:
                    await account.connect()
                    if isinstance(i, str):
                        if invite_chat.message.count('/+') == 0:
                            response = await add_user(account, invite_chat.message, i)
                            if response['added']:
                                invited_count += 1

                    arr2.remove(i)
            await bot_client.send_message(SENDER, 'Успешно приглашено ' + number.message + ' пользователей')

    await bot_client.run_until_disconnected()


asyncio.run(main())
