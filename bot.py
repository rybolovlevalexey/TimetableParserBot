import telebot
import peewee as pw
import choose_group_handlers
from models import User, EducationalDirection, GroupDirection
from parsing import week_timetable_dict, removing_unnecessary_items, \
    make_one_day_schedule, make_week_schedule
from datetime import datetime, timedelta
import re
import json
import typing
from main import *
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

db = pw.SqliteDatabase("db.sqlite3")  # база данных с пользователями и ссылками на группы
bot = telebot.TeleBot(open("personal information/personal information.txt").readlines()[0].strip())


def database_cleaning():
    # выполнять каждый раз при тестировании и создании бота
    db.drop_tables([User])
    db.create_tables([User])
    print("Table User in database has been cleared and recreated")


@bot.message_handler(commands=["start"])
def start_message(message: telebot.types.Message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=False)
    markup.row(telebot.types.KeyboardButton("На сегодня"),
               telebot.types.KeyboardButton("На завтра"))
    markup.row(telebot.types.KeyboardButton("На текущую неделю"),
               telebot.types.KeyboardButton("На следующую неделю"))
    bot.send_message(message.chat.id, "Бот начал работу", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in
                            ["Оставить выбранную группу", "Начать регистрацию сначала",
                             "Продолжить заполнение"])
def choose_group_one_more_time(callback: telebot.types.CallbackQuery):
    mes_text = str(callback.data)
    mes_id, chat_id, us_id = callback.message.id, callback.message.chat.id, callback.from_user.id

    if mes_text == "Оставить выбранную группу":
        group_name = list(elem.group_number for elem in User.select().where(User.user_id == us_id))
        bot.send_message(chat_id=chat_id, text=f"Ваша группа остаётся прежней {group_name[0]}")
    elif mes_text == "Начать регистрацию сначала":
        query = User.update(group_url="default_url", admission_year="default_year",
                            user_faculty="default_faculty", group_number="default_group_number",
                            education_degree="default_degree",
                            education_program="default_program").where(User.user_id == us_id)
        query.execute()
        bot.send_message(chat_id=chat_id, text=f"Регистрация начата заново")
        choose_group_message_begin_again(callback)
    elif mes_text == "Продолжить заполнение":
        pass


def choose_group_message_begin_again(callback: telebot.types.CallbackQuery):
    # начало добавления группы пользователя при получении не /сообщения, а callback
    markup = telebot.types.InlineKeyboardMarkup()
    for ind in range(0, len(YEARS), 2):
        year = YEARS[ind]
        if year + 1 in YEARS:
            markup.row(telebot.types.InlineKeyboardButton(text=str(year), callback_data=str(year)),
                       telebot.types.InlineKeyboardButton(text=str(year + 1),
                                                          callback_data=str(year + 1)))
        else:
            markup.row(telebot.types.InlineKeyboardButton(text=str(year), callback_data=str(year)))
    bot.send_message(callback.message.chat.id,
                     "Выберите год вашего поступления на текущее направление",
                     reply_markup=markup)


@bot.message_handler(commands=["choose_group"])
def choose_group_message_begin(message: telebot.types.Message):
    # проверка - есть ли уже в базе пользователь
    us_id = message.from_user.id
    chat_id = message.chat.id
    result = list(elem for elem in User.select().where(User.user_id == us_id))
    if len(result) == 1 and result[0].admission_year != "default_year":
        res: User = result[0]
        if res.group_url != "default_url" and res.group_number != "default_group_number":
            # пользователь уже прошёл полную регистрацию
            text1 = "Оставить выбранную группу"
            text2 = "Начать регистрацию сначала"
            text_main = "Вы уже проходили регистрацию и информация " \
                        "о вашей группе уже сохранена. Хотите удалить эти данные и " \
                        "начать регистрацию заново?"
        else:
            # пользователь не закончил прохождение регистрации
            text1 = "Продолжить заполнение"
            text2 = "Начать регистрацию сначала"
            text_main = "Вы уже проходили регистрацию, поэтому у нас есть некоторая " \
                        "информация о вас."
        mark = InlineKeyboardMarkup().row(InlineKeyboardButton(text=text1, callback_data=text1),
                                          InlineKeyboardButton(text=text2, callback_data=text2))
        bot.send_message(chat_id, text_main, reply_markup=mark)
    else:
        # начало добавления группы пользователя
        markup = telebot.types.InlineKeyboardMarkup()
        for year in range(2020, 2024, 2):
            markup.row(telebot.types.InlineKeyboardButton(text=str(year), callback_data=str(year)),
                       telebot.types.InlineKeyboardButton(text=str(year + 1),
                                                          callback_data=str(year + 1)))
        bot.send_message(message.chat.id,
                         "Выберите год вашего поступления на текущее направление",
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.isdigit() and len(call.data) == 4)
@bot.callback_query_handler(func=lambda call: call.data in INSTITUTE_FACULTIES or
                            call.data in EDUCATION_DEGREES or call.data in EDUCATION_PROGRAMS_SHORT)
@bot.callback_query_handler(
    func=lambda call: re.search(r"\b[0-9][0-9]\.[БМ][0-9][0-9]-[а-я]+", call.data) is not None)
def choose_group_message(callback: telebot.types.CallbackQuery):
    if callback.data.isdigit() and len(callback.data) == 4:
        choose_group_handlers.callback_year(bot=bot, callback=callback)
    elif callback.data in INSTITUTE_FACULTIES:
        choose_group_handlers.callback_faculty(bot=bot, callback=callback)
    elif callback.data in EDUCATION_DEGREES:
        choose_group_handlers.callback_degree(bot=bot, callback=callback)
    elif callback.data in EDUCATION_PROGRAMS_SHORT:
        choose_group_handlers.callback_program(bot=bot, callback=callback)
    elif re.search(r"\b[0-9][0-9]\.[БМ][0-9][0-9]-[а-я]+", callback.data) is not None:
        choose_group_handlers.callback_group_name(bot=bot, callback=callback)


# choos_subgr-(информация о действии: start - начало обработки,
# выбранная подгруппа - id группы из соответствующей таблицы бд,
# ни одна из этих подгрупп - none_of_these)
# Предоставление сообщения с выбором подгрупп
@bot.callback_query_handler(func=lambda
        call: str(call.data).startswith("choos_subgr"))
def callback_start_choosing_subgroups(callback: telebot.types.CallbackQuery):
    us_id, mes_id = callback.from_user.id, callback.message.id
    json_file = open(f"duplicate_items/{us_id}.json", "r+")
    json_data = json.load(json_file)
    mode_callback = callback.data.split("-")[1]
    if mode_callback == "start":
        for day_key in json_data.keys():
            for time_key in json_data[day_key]["Is checked"].keys():
                json_data[day_key]["Is checked"][time_key] = False
    flag = False
    for day_key in json_data.keys():
        for time_key in json_data[day_key]["Is checked"].keys():
            if json_data[day_key]["Is checked"][time_key]:
                continue
            markup = telebot.types.InlineKeyboardMarkup()
            for elem in json_data[day_key][time_key]:
                btn_text = (elem[1] + elem[3])[:60]
                btn_data = ""  # не забыть исправить
                markup.add(telebot.types.InlineKeyboardButton(text=btn_text,
                                                              callback_data=btn_data))
            markup.add(telebot.types.InlineKeyboardButton(text="Ни одна из этих подгрупп",
                                                          callback_data=
                                                          "choos_subgr-none_of_these"))
            bot.edit_message_text(f"День {day_key} время {time_key}",
                                  callback.message.chat.id, mes_id, reply_markup=markup)
            flag = True
            break
        if flag:
            break


@bot.callback_query_handler(func=lambda call: call.data in SETTINGS_CALLBACKS)
def callback_from_settings(callback: telebot.types.CallbackQuery):
    text = callback.data
    us_id, mes_id = callback.from_user.id, callback.message.id
    url = list(elem.group_url for elem in User.select().where(User.user_id == us_id))[0]
    schedule = week_timetable_dict(url)
    duplicate_items: dict[str: dict[str: list[str]]] = dict()

    if text == "Close settings":
        bot.delete_message(callback.message.chat.id, mes_id - 1)
        bot.delete_message(callback.message.chat.id, mes_id)
    elif text == "Delete account":
        # cделать удаление аккаунта
        pass
    elif text == "Choosing subgroup":  # открытие окна с выбором подгрупп дублирующихся предметов
        for key, value in schedule.items():
            # key - день недели с датой, value - список с расписанием в этот день
            k = key.split(", ")[0]
            # добавление каждого дня как ключа в словарь дубликатов, и в каждый день по ключу
            # Is checked cловаря с флагами на каждое время
            duplicate_items[k]: dict[str, dict[str, typing.Union[list[list[str]],
                                                                 dict[str, bool]]]] = dict()
            duplicate_items[k]["Is checked"]: dict[str, bool] = dict()

            for i in range(len(value) - 1):  # проход по расписанию в день key
                if (i == 0 and value[i][0] == value[i + 1][0]) or \
                        (i > 0 and value[i][0] == value[i + 1][0] and
                         value[i - 1][0] != value[i][0]):
                    # value[i][0] - время проведения
                    if value[i][0] not in duplicate_items[k].keys():
                        # создание списка, если в день key и время value[i][0] не было дубликатов
                        duplicate_items[k][value[i][0]] = list()
                        # создание флага для дня key и времени value[i][0], с целью узнать
                        # было ли эта информация уже обработана пользователем
                        duplicate_items[k]["Is checked"][value[i][0]] = False
                    duplicate_items[k][value[i][0]].append(value[i])
                    duplicate_items[k][value[i][0]].append(value[i + 1])
                elif i > 0 and value[i][0] == value[i + 1][0] and value[i - 1][0] == value[i][0]:
                    if value[i][0] not in duplicate_items[k].keys():
                        duplicate_items[k][value[i][0]] = list()
                    duplicate_items[k][value[i][0]].append(value[i + 1])
        json.dump(duplicate_items, open(f"duplicate_items/{us_id}.json", "w"), indent=4)
        markup = telebot.types.InlineKeyboardMarkup(). \
            add(telebot.types.InlineKeyboardButton("Начать",
                                                   callback_data="choos_subgr-start"))
        bot.edit_message_text("Выберите ваши подгруппы в дублирующихся предметах вашей группы.",
                              callback.message.chat.id, callback.message.id, reply_markup=markup)
    else:
        pass


# присылает в ответ сообщение с возможными настройками; добавлять их по мере роста функционала
@bot.message_handler(commands=["settings"])
def settings_message(message: telebot.types.Message):
    markup = telebot.types.InlineKeyboardMarkup()
    # выбор своей подгруппы в дублирующихся предметах
    markup.row(telebot.types.InlineKeyboardButton(text="Choosing subgroup",
                                                  callback_data="Choosing subgroup"))
    markup.row(telebot.types.InlineKeyboardButton(text="Delete account",
                                                  callback_data="Delete account"))
    markup.row(telebot.types.InlineKeyboardButton(text="Close", callback_data="Close settings"))
    bot.send_message(message.chat.id, "Настройки бота", reply_markup=markup)


@bot.message_handler()
def take_message(message: telebot.types.Message):
    user_full_name = message.from_user.full_name
    us_id, user_login = message.from_user.id, message.from_user.username
    # проверка, есть ли такой пользователь в базе данных
    is_user_registred = False
    for elem in User.select():
        if str(elem.user_id) == str(us_id):
            is_user_registred = True
            break
    if not is_user_registred:
        bot.send_message(message.chat.id, "Вы не зарегистрированы, "
                                          "сделать это можно, используя команду /choose_group")
        return None
    url = list(elem.group_url for elem in User.select().where(User.user_id == us_id))[0]

    if message.text == "На сегодня":
        schedule = removing_unnecessary_items(week_timetable_dict(url))
        day, month, year = str(datetime.today()).split()[0].split("-")[::-1]
        bot.send_message(message.chat.id, make_one_day_schedule(schedule, day), parse_mode="html")
    elif message.text == "На завтра":
        schedule = removing_unnecessary_items(week_timetable_dict(url))
        day, month, year = str(datetime.today().date() +
                               timedelta(days=1)).split()[0].split("-")[::-1]
        bot.send_message(message.chat.id, make_one_day_schedule(schedule, day), parse_mode="html")
    elif message.text == "На текущую неделю":
        schedule = removing_unnecessary_items(week_timetable_dict(url))
        bot.send_message(message.chat.id, make_week_schedule(schedule), parse_mode="html")
    elif message.text == "На следующую неделю":
        schedule = removing_unnecessary_items(week_timetable_dict(url, next_week=True))
        bot.send_message(message.chat.id, make_week_schedule(schedule), parse_mode="html")


if __name__ == "__main__":
    database_cleaning()
    bot.polling(none_stop=True)
