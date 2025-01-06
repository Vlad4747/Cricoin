

import sys,os

from settings import *
from functions import *
from messages import *
from data import *
import time
import random


from aiogram import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.exceptions import BotBlocked
import asyncio
from aiogram.utils.exceptions import Unauthorized
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
import traceback


loop = asyncio.get_event_loop()

bot = Bot(token = token, loop = loop)


dp = Dispatcher(bot, storage = MemoryStorage())

dp.middleware.setup(LoggingMiddleware())

main_menu = ReplyKeyboardMarkup(resize_keyboard = True)
main_menu.add('💰 Заработать', '📢 Рекламировать')
main_menu.add('👤 Профиль','🔗 Полезные ссылки')

admin_menu = InlineKeyboardMarkup()
statistics_bt = InlineKeyboardButton(text = '📊 Статистика', callback_data = 'stat')
mail_bt = InlineKeyboardButton(text = '✉️ Рассылка', callback_data = 'mail')
give_uban_bt = InlineKeyboardButton(text = '🚷 Выдать бан/разбан', callback_data = 'uban')
change_balance_bt = InlineKeyboardButton(text = '💳 Изменить баланс', callback_data = 'chb')
list_of_additional_commands = InlineKeyboardButton(text="Список дополнительных команд", callback_data='list_addi_commands')
admin_menu.add(statistics_bt, mail_bt)
admin_menu.add(give_uban_bt, change_balance_bt)
admin_menu.add(list_of_additional_commands)

cancel_menu = InlineKeyboardMarkup()
cancel_bt = InlineKeyboardButton(text = '🚫 Отмена', callback_data = 'cancel')
cancel_menu.add(cancel_bt)

earnings_menu = InlineKeyboardMarkup()
earnings_menu.add(InlineKeyboardButton(text="📢 Подписатся на канал",callback_data="SUB_CHANNELS"))
earnings_menu.add(InlineKeyboardButton(text="👁 Посмотреть пост",callback_data="VIEW_POSTS"))

ads_menu = InlineKeyboardMarkup()
ads_menu.add(InlineKeyboardButton(text="📢 Канал",callback_data="add_channel"),InlineKeyboardButton(text="👁 пост",callback_data="add_post"))

next_post_menu = InlineKeyboardMarkup()
next_post_menu.add(InlineKeyboardButton(text="Следущий пост",callback_data="next_post"))

old_m = None



class UserStates(Helper):
    GET_CHANNEL_TO_UP = ListItem()
    GET_SUB_COUNT = ListItem()
    CONFIRMATION = ListItem()
    GET_MSG_FOR_MAIL = ListItem()
    GET_USER_FOR_UBAN = ListItem()
    GET_USER_FOR_CHB = ListItem()
    GET_VIEW_COUNT = ListItem()
    GET_POST = ListItem()
async def checks():
    print("tick")



@dp.message_handler(state='GET_USER_FOR_CHB')
async def handle_user_for_chb(m: types.Message):
    list = m.text.split(' ')
    if len(list) == 2:
        id = int(list[0])
        value = int(list[1])
        state = dp.current_state(user=m.from_user.id)
        try:
            users[id]["balance"] += value
            await m.reply(f"Вы выдали {value} Cricoins")
            await bot.send_message(id,f"Вам выдали {value} Cricoins")
            await state.reset_state()
        except:
            await m.reply(f"Ошибка!")
            await state.reset_state()
        save()
@dp.message_handler(state='GET_USER_BAN')
async def handle_user_for_chb(m: types.Message):
    list = m.text.split(' ')
    if len(list) == 1:
        id = int(list[0])
        state = dp.current_state(user=m.from_user.id)
        if not id in black_list:
            if id in users:
                black_list.append(id)
                await m.reply("Выдан бан")
            else:
                black_list.append(id)
                await m.reply("Бан выдан, но этого id нет в базе")
        else:
            black_list.pop(id)
            await m.reply("разбанен")
        save()
@dp.message_handler(state = 'GET_CHANNEL_TO_UP')
async def channel_to_up_handle(m: types.Message):
    print(m.text)
    try:
        if m.content_type == 'text':
            my_id = await bot.get_me()
            text = m.text
            if text.startswith("https://t.me/"):
                text = '@' + text.replace("https://t.me/",'')
            print(text)
            get_channel = await bot.get_chat(text)

            if get_channel.type == 'channel':
                status_bot_in_channel = await bot.get_chat_member(chat_id = text, user_id = my_id.id)
                if not get_channel.id in channels or not channels[get_channel.id]["subs_count"] > 0:
                    if status_bot_in_channel.status == 'administrator':
                        number = save_channel(id=get_channel.id,username=get_channel.username, writer = m.from_user.id)
                        print(number)
                        cancel_promotion = InlineKeyboardMarkup()
                        cancel_promotion.add(InlineKeyboardButton(text = '🚫 Отмена', callback_data = 'cancel_' + str(number)))
                        await bot.delete_message(message_id = m.message_id  - 1, chat_id = m.from_user.id)
                        await m.reply(SEND_SUB_COUNT_1(m), parse_mode = 'Markdown', reply_markup = cancel_promotion)
                        state = dp.current_state(user = m.from_user.id)

                        await state.set_state('GET_SUB_COUNT')
                    else:
                        await bot.delete_message(message_id = m.message_id  - 1, chat_id = m.from_user.id)
                        await m.reply(BOT_NOT_IN_CHANNEL, parse_mode = 'Markdown', reply_markup = cancel_menu)
                else:
                    await m.reply(CHANNEL_ON_PROMOTION_2, reply_markup = cancel_menu)
            else:
                await bot.delete_message(message_id = m.message_id  - 1, chat_id = m.from_user.id)
                await m.reply(THIS_IS_NOT_CHANNEL, parse_mode = 'Markdown', reply_markup = cancel_menu)
        else:
            await m.reply(THIS_IS_NOT_TEXT, parse_mode = 'Markdown', reply_markup = cancel_menu)
    except Exception as e:
        await m.reply(f"Ошибка: {e}", reply_markup=cancel_menu)
@dp.message_handler(content_types = ['text', 'video', 'photo', 'document', 'animation'], state = 'GET_POST')
async def post_handle(m: types.Message):
    state = dp.current_state(user=m.from_user.id)
    await state.reset_state()
    users[m.from_user.id]["p1"] = m.message_id
    await state.set_state('GET_VIEW_COUNT')
    await m.reply(f'''Отправте сколько человек увидит ваш пост
1 просмотр = {VIEW_PRICE} Cricoins

максимум для вашего баланса: {user_balance(m.from_user.id) // VIEW_PRICE}
''')
@dp.message_handler(state = 'GET_VIEW_COUNT')
async def get_post_count(m: types.Message):
    try:
        if m.content_type == 'text' and (m.text.isdigit() == True) and (int(m.text) >= LITTLE_SUBCOIN_TO_GET_VIEWS and user_balance(m.from_user.id) // VIEW_PRICE >= int(m.text)):
            print(m.text)
            post = add_post(id=users[m.from_user.id]["p1"],count=int(m.text),writer=m.from_user.id)
            print(post)
            confirmation_menu = InlineKeyboardMarkup()
            confirmation_menu.add(InlineKeyboardButton(text='🚫 Отмена', callback_data='cancel__' + str(post["id"])),
                                  InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm_2'))
            state = dp.current_state(user=m.from_user.id)
            await state.set_state('CONFIRMATION')
            await bot.delete_message(message_id=m.message_id - 1, chat_id=m.from_user.id)

            if not post in [None, 0]:
                await m.reply(CONFIRM_ADDING_POST(subcount=post["count"],price=post["count"] * VIEW_PRICE),reply_markup=confirmation_menu)
            else:
                await m.reply("Ошибка", reply_markup=cancel_menu)
        else:
            cancel_wnum_menu = InlineKeyboardMarkup()
            cancel_wnum_menu.add(InlineKeyboardButton(text='🚫 Отмена', callback_data='cancel'))
            await m.reply(LITTLE_SUBCOIN_2, reply_markup=cancel_wnum_menu)
    except Exception as e:
        await m.reply(f"Ошибка: {e}", reply_markup=cancel_menu)
@dp.message_handler(state = 'GET_SUB_COUNT')
async def channel_to_up_handle(m: types.Message):
    try:
        if m.content_type == 'text' and (m.text.isdigit() == True) and (int(m.text) >= LITTLE_SUBCOIN_TO_GET_SUBS) and user_balance(m.from_user.id)//SUB_PRICE >= int(m.text):
            print(m.text)
            channel = save_channel(subs_count=int(m.text), writer=m.from_user.id)
            confirmation_menu = InlineKeyboardMarkup()
            confirmation_menu.add(InlineKeyboardButton(text='🚫 Отмена', callback_data='cancel_'+str(channel["id"])),
                                  InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm_'+str(channel["id"])))
            state = dp.current_state(user=m.from_user.id)
            await state.set_state('CONFIRMATION')
            await bot.delete_message(message_id=m.message_id - 1, chat_id=m.from_user.id)
            print(channel)
            if not channel in [None,0]:
                await m.reply(CONFIRM_ADDING_CHANNEL(username=channel["username"], subcount=channel["subs_count"], price=channel["subs_count"]*SUB_PRICE),reply_markup=confirmation_menu)
            else:
                await m.reply("Ошибка",reply_markup=cancel_menu)
        else:
            cancel_wnum_menu = InlineKeyboardMarkup()
            cancel_wnum_menu.add(InlineKeyboardButton(text='🚫 Отмена', callback_data='cancel'))
            await m.reply(LITTLE_SUBCOIN_2, reply_markup=cancel_wnum_menu)
    except Exception as e:
        await m.reply(f"Ошибка: {e}", reply_markup=cancel_menu)
@dp.message_handler(commands = ['start','help'])
async def start_commands_handle(m: types.Message):
    if not m.from_user.id in users:
        argument = m.get_args()
        print(m.from_user.id,argument)
        if (argument != None) and (argument.isdigit() == True) and int(argument) in users:
            users[int(argument)]["balance"] += REF_BONUS
            users[int(argument)]["referals"].append(m.from_user.id)
            add_user(m.from_user.id,argument)
            users[m.from_user.id]["ref_father"] = int(argument)
            await m.reply(START, reply_markup = main_menu)
            await bot.send_message(text = NEW_REFERAL(int(argument)), chat_id = argument)
        else:
            add_user(m.from_user.id)
            await m.reply(START, reply_markup = main_menu)
    else:
        await m.reply(UPDATE, reply_markup = main_menu)
@dp.message_handler(commands = ['get_base'])
async def start_commands_handle(m: types.Message):
    await m.reply(text=data)
    print(data)
@dp.message_handler(commands = ['get_black_list'])
async def start_commands_handle(m: types.Message):
    if len(black_list) > 0:
        print(list_to_table(black_list))
        await m.reply(text=list_to_table(black_list))
    else:
        await m.reply(text="Список пуст")
@dp.message_handler(commands = ['admin'])
async def start_commands_handle(m: types.Message):
    if m.from_user.id in admins:
        await m.reply(SELECT_ADMIN_MENU_BUTTON,reply_markup=admin_menu)
    else:
        await m.reply(YOU_WAS_HACK_ME)
@dp.message_handler(lambda m: m.text == '👤 Профиль' and user_banned(m.from_user.id) == False)
async def profile_button_handle(m: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="👣 Партнёрская программа",callback_data='PARTNER_PROGRAM'))
    await m.reply(PROFILE(m),reply_markup=markup)
@dp.message_handler(lambda m: m.text == '💰 Заработать' and not user_banned(m.from_user.id))
async def earning_button_handle(m: types.Message):
    global old_m
    msg = await m.reply('''Выберите как хотите зарабатывать: 👇

📢 Подписатся на канал.

👁 смотреть посты.''',reply_markup=earnings_menu)
    old_m = msg.message_id
@dp.message_handler(lambda m: m.text == '🔗 Полезные ссылки' and user_banned(m.from_user.id) == False)
async def links_button_handle(m: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Правила и инструкция",url=LINK_TO_INTRODUCTION_AND_RULES))
    markup.add(InlineKeyboardButton(text="Cricoin | News",url=LINK_TO_CHANNEL_OF_BOT))
    markup.add(InlineKeyboardButton(text="Cricoin | Chat",url=LINK_TO_CHAT_OF_BOT))
    await m.reply(USEFUL_LINKS,reply_markup=markup, parse_mode = 'Markdown')
@dp.message_handler(lambda m: m.text == '📢 Рекламировать' and user_banned(m.from_user.id) == False)
async def ads_button_handle(m: types.Message):
    global old_m
    msg = await m.reply(f'''Выберите что хотите рекламировать

баланс: {user_balance(m.from_user.id)} Cricoins''',reply_markup=ads_menu)
    old_m = msg.message_id
@dp.callback_query_handler(lambda c: 'confirm_' in c.data, state = 'CONFIRMATION')
async def confirm_button_handler(c :types.callback_query):
    number = int(c.data.replace('confirm_', ''))

    if number < 0:
        users[c.from_user.id]["balance"] -= SUB_PRICE * channels[number]["subs_count"]
        await c.message.edit_text(CHANNEL_SUCCESSFULLY_ADED)
        state = dp.current_state(user = c.from_user.id)
        await state.reset_state()
    elif number == 2:
        users[c.from_user.id]["balance"] -= VIEW_PRICE * posts[str(users[c.from_user.id]["p1"])+'_'+str(c.from_user.id)]["count"]
        await c.message.edit_text(POST_SUCCESSFULLY_ADED)
        state = dp.current_state(user=c.from_user.id)
        await state.reset_state()
    else:
        #await c.message.edit_text(luck)
        await bot.delete_message(c.from_user.id,c.message.message_id)
        state = dp.current_state(user = c.from_user.id)
        await state.reset_state()
@dp.callback_query_handler(lambda c: 'cancel_' in c.data, state = ['CONFIRMATION', 'GET_SUB_COUNT'])
async def cancel_wnum_button_handler(c: types.callback_query):
    number = c.data.replace('cancel_', '')
    try:
        status = int(number)
        if status == 0:
            await c.message.edit_text(CHANNEL_ON_PROMOTION)
            state = dp.current_state(user = c.from_user.id)
            await state.reset_state()
        elif status < 0:
            channels.pop(status)
            await c.message.edit_text(CANCEL_TEXT)
            state = dp.current_state(user=c.from_user.id)
            await state.reset_state()
        else:
            await c.message.edit_text(CANCEL_TEXT)
            state = dp.current_state(user = c.from_user.id)
            await state.reset_state()
    except:
        number = number.replace('_','')
        status = int(number)
        if status > 0:
            posts.pop(str(status)+'_'+str(c.from_user.id))
            await c.message.edit_text(CANCEL_TEXT)
            state = dp.current_state(user=c.from_user.id)
            await state.reset_state()
@dp.callback_query_handler(lambda c: c.data == 'chb')
async def chb(c: types.CallbackQuery):
    await c.message.edit_text(SEND_USER_FOR_CHANGE_BALANCE(c))
    state = dp.current_state(user=c.from_user.id)
    await state.set_state('GET_USER_FOR_CHB')
    print(users)
@dp.callback_query_handler(lambda c: c.data == 'uban')
async def uban(c: types.CallbackQuery):
    await c.message.edit_text(SEND_USER_FOR_CHANGE_BALANCE(c))
    state = dp.current_state(user=c.from_user.id)
    await state.set_state('GET_USER_BAN')
@dp.callback_query_handler(lambda c: c.data == 'list_addi_commands')
async def list_addi_commands(c: types.CallbackQuery):
    await bot.delete_message(c.from_user.id,c.message.message_id)
    if c.from_user.id in admins:
        await bot.send_message(c.from_user.id,LIST_OF_ADDITIONAL_COMMANDS)
@dp.callback_query_handler(lambda c: c.data == 'add_channel')
async def add_channel(c: types.CallbackQuery):
    await bot.delete_message(c.from_user.id,c.message.message_id)
    await bot.send_message(c.from_user.id,GIVE_CHANNEL_LINK,)
    state = dp.current_state(user=c.from_user.id)
    await state.set_state('GET_CHANNEL_TO_UP')
@dp.callback_query_handler(lambda c: c.data == 'add_post')
async def add_channel(c: types.CallbackQuery):
    await bot.delete_message(c.from_user.id,c.message.message_id)
    await bot.send_message(c.from_user.id,GIVE_POST)
    state = dp.current_state(user=c.from_user.id)
    await state.set_state('GET_POST')
@dp.callback_query_handler(lambda c: c.data == 'SUB_CHANNELS')
async def sub_channels(c: types.CallbackQuery):
    await bot.delete_message(c.from_user.id,c.message.message_id)
    print(1)
    b_list = []
    for i in range(70):
        print(9)
        channels_list = channel_for_subscribe(c.from_user.id)

        if channels_list != 0 and len(channels_list) > len(b_list):
            print(10)
            channel_to_subscribe = random.choice(list(channels_list))
            channel = channels[channel_to_subscribe]
            if (not channel_to_subscribe  in b_list) and (not c.from_user.id in channel["subscriptions"]) and (len(channel["subscriptions"])<channel["subs_count"]):
                print(channels_list,b_list)
                my_id = await bot.get_me()
                try:
                    bot_status = await bot.get_chat_member(user_id=bot_id, chat_id=channel_to_subscribe)
                    bot_status = bot_status.status
                    print(bot_status)
                except (Unauthorized, BotBlocked):
                    bot_status = 'left'
                except:
                    await bot.send_message(c.from_user.id, NO_HAVE_CHANNELS_FOR_SUBSCRIBE)
                    break

                if bot_status == "administrator":
                    status_of_user = await bot.get_chat_member(user_id=c.from_user.id, chat_id=channel_to_subscribe)
                    print(status_of_user.status)
                    if status_of_user.status == 'left':
                        username = await bot.get_chat(chat_id=channel_to_subscribe)
                        subscribe_menu = InlineKeyboardMarkup()
                        subscribe_menu.add(InlineKeyboardButton(text='Перейти к каналу',
                                                                url='tg://resolve?domain=' + username.username))
                        print(channels_list,channel_to_subscribe)
                        subscribe_menu.add(InlineKeyboardButton(text='Проверить подписку', callback_data='sub_' + str(channel_to_subscribe)))
                        await bot.send_message(c.from_user.id, SUBSCRIBE_ON_THIS_CHANNEL, reply_markup=subscribe_menu)
                        break
                    else:
                        b_list.append(channel_to_subscribe)
                        print("bl",b_list,channel_to_subscribe)
                else:
                    writer = get_writer(channel_to_subscribe)
                    id = channel_to_subscribe
                    if writer != 0:
                        await bot.send_message(writer, CHANNEL_WAS_DEL_FROM_CHANNEL(id, LINK_TO_INTRODUCTION_AND_RULES))
        else:
            await bot.send_message(c.from_user.id, NO_HAVE_CHANNELS_FOR_SUBSCRIBE)
            break
    await bot.send_message(c.from_user.id, NO_HAVE_CHANNELS_FOR_SUBSCRIBE)
@dp.callback_query_handler(lambda c: c.data == "VIEW_POSTS")
async def sub_channels(c: types.CallbackQuery):
    await bot.delete_message(c.from_user.id,c.message.message_id)
    posts_list = posts_for_view(c.from_user.id)
    for i_ in range(70):
        post = random.choice(posts_list)
        try:
            print(post)
            if post["count"] > 0 and len(post["views"]) < post["count"]:
                await bot.send_message(c.from_user.id,"Пролистайте ленту вверх,вниз⬆️⬇️")
                await bot.forward_message(chat_id=c.from_user.id,from_chat_id=post["writer"],message_id=post["id"])
                await bot.send_message(c.from_user.id, "⏳")
                await asyncio.sleep(5)
                users[c.from_user.id]["balance"] += VIEW_PRICE
                posts[str(post["id"])+'_'+str(post["writer"])]["views"].append(c.from_user.id)
                save()
                await bot.send_message(c.from_user.id,NEXT_POST(c),reply_markup=next_post_menu)
                return
        except:
            exc_type, _, exc_tb = sys.exc_info()
            fname = traceback.extract_tb(exc_tb)[-1].filename
            line = traceback.extract_tb(exc_tb)[-1].lineno
            print(f"Тип исключения: {exc_type}")
            print(f"Имя файла: {fname}")
            print(f"Номер строки: {line}")
    await bot.send_message(c.from_user.id, "❌ Больше нет постов для просмотра")
@dp.callback_query_handler(lambda c: 'sub_' in c.data)
async def check_user_in_channel(c: types.CallbackQuery):
    number = int(c.data.replace('sub_', ''))
    my_id = await bot.get_me()
    try:
        bot_status = await bot.get_chat_member(chat_id=number, user_id=my_id.id)
        bot_status = bot_status.status
    except (Unauthorized, BotBlocked):
        bot_status = 'left'
    if bot_status == "administrator":
        status_of_user = await bot.get_chat_member(user_id=c.from_user.id, chat_id=number)
        get_channel = await bot.get_chat(number)
        username = get_channel.username
        print(status_of_user.status)
        if status_of_user.status != 'left':
            users[c.from_user.id]["balance"] += SUB_PRICE
            channels[get_channel.id]["subscriptions"].append(c.from_user.id)
            await c.message.edit_text(SUBSCRIBE_IS_SUCCESSFULLY(username))
            save()
        else:
            await bot.send_message(c.from_user.id,YOU_DONT_COMPLETE_SUBS)
    else:
        writer = get_writer(number)
        id = number
        if writer != 0:
            await bot.send_message(writer, CHANNEL_WAS_DEL_FROM_CHANNEL(id, LINK_TO_INTRODUCTION_AND_RULES))
@dp.callback_query_handler(lambda c: c.data == 'PARTNER_PROGRAM')
async def referal_button_handle(c: types.CallbackQuery):
    await bot.delete_message(c.from_user.id, c.message.message_id)
    get_bot = await bot.get_me()
    await bot.send_message(c.from_user.id,PARTNER_PROGRAM(get_bot.username, c.from_user.id, len(referals(c.from_user.id))))
@dp.callback_query_handler(lambda c: c.data == 'cancel', state = UserStates.all())
async def cancel_button_handle(c: types.callback_query):
    try:
        await c.message.edit_text(CANCEL_TEXT)
        state = dp.current_state(user = c.from_user.id)
        await state.reset_state()
    except:
        print(sys.exc_info())
@dp.callback_query_handler(lambda c: c.data == "next_post")
async def next_post(c: types.CallbackQuery):
    await bot.delete_message(c.from_user.id, c.message.message_id)
    posts_list = posts_for_view(c.from_user.id)
    for i_ in range(30):
        post = random.choice(posts_list)
        try:
            print(post)
            if post["count"] > 0 and len(post["views"]) < post["count"]:
                await bot.send_message(c.from_user.id, "Пролистайте ленту вверх,вниз⬆️⬇️")
                await bot.forward_message(chat_id=c.from_user.id, from_chat_id=post["writer"], message_id=post["id"])
                await bot.send_message(c.from_user.id, "⏳")
                await asyncio.sleep(3)
                users[c.from_user.id]["balance"] += VIEW_PRICE
                posts[str(post["id"]) + '_' + str(post["writer"])]["views"].append(c.from_user.id)
                save()
                await bot.send_message(c.from_user.id, NEXT_POST(c), reply_markup=next_post_menu)
                return
        except:
            exc_type, _, exc_tb = sys.exc_info()
            fname = traceback.extract_tb(exc_tb)[-1].filename
            line = traceback.extract_tb(exc_tb)[-1].lineno
            print(f"Тип исключения: {exc_type}")
            print(f"Имя файла: {fname}")
            print(f"Номер строки: {line}")

    await bot.send_message(c.from_user.id, "❌ Больше нет постов для просмотра")
async def on_shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True, on_shutdown = on_shutdown, loop = loop)