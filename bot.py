import telebot
import peewee as pw
from models import User, EducationalDirection, GroupDirection
from parsing import week_timetable_dict, removing_unnecessary_items
from datetime import datetime, timedelta
import re
from pprint import pprint
import json

db = pw.SqliteDatabase("db.sqlite3")  # база данных с пользователями и ссылками на группы
bot = telebot.TeleBot(open("personal information.txt").readlines()[2].strip())  # подключение к боту
flags_dict: dict[str, bool] = dict()
flags_dict["choosing_group_flag"] = False
INSTITUTE_FACULTIES = ["Мат-мех"]  # список с факультетами, необходимо расширить в будущем
EDUCATION_DEGREES = ["Бакалавриат", "Магистратура"]  # список степеней образования
EDUCATION_PROGRAMS = sorted(set(elem.name for elem in EducationalDirection.select()))
EDUCATION_PROGRAMS_SHORT = list(map(lambda x: x[:60], EDUCATION_PROGRAMS))
SETTINGS_CALLBACKS = ["Close settings", "Choosing subgroup"]  # возможны колбэки от сообщения с настройками


# выполнять каждый раз при тестировании и создании бота
db.drop_tables([User])
db.create_tables([User])
print("Database has been cleared and recreated")


@bot.callback_query_handler(func=lambda call:
re.search(r"\b[0-9][0-9]\.[БМ][0-9][0-9]-[а-я]+", call.data) is not None)
def callback_group_name(callback: telebot.types.CallbackQuery):
    group_name = callback.data
    us_id = callback.from_user.id
    User.update(group_number=group_name).where(User.user_id == us_id).execute()
    bot.send_message(callback.message.chat.id, f"Ваша группа - {group_name}. "
                                               f"Информация о вашей группе сохранена")
    url = list(elem.url for elem in
               GroupDirection.select().
               where(GroupDirection.group_name == group_name))[0]
    User.update(group_url=url).where(User.user_id == us_id).execute()


@bot.callback_query_handler(func=lambda call: call.data in EDUCATION_PROGRAMS_SHORT)
def callback_program(callback: telebot.types.CallbackQuery):
    program = callback.data
    bot.send_message(callback.message.chat.id, f"Ваше направление образования - {program}")
    us_id = callback.from_user.id
    User.update(education_program=program).where(User.user_id == us_id).execute()
    program_name = list(elem for elem in EDUCATION_PROGRAMS if str(elem).startswith(program))[0]
    year = list(elem.admission_year for elem in User.select().where(User.user_id == us_id))[0]

    prog_id = list(elem.id for elem in EducationalDirection.select().where(
        (EducationalDirection.name == program_name) & (EducationalDirection.year == year)))[0]
    available_groups = list(elem.group_name for elem in GroupDirection.select().where(
        GroupDirection.educational_program_id == prog_id))
    markup = telebot.types.InlineKeyboardMarkup()
    for i in range(0, len(available_groups), 2):
        if i + 1 == len(available_groups):
            markup.row(telebot.types.InlineKeyboardButton(available_groups[i]))
        else:
            markup.row(telebot.types.InlineKeyboardButton(text=available_groups[i],
                                                          callback_data=available_groups[i]),
                       telebot.types.InlineKeyboardButton(text=available_groups[i + 1],
                                                          callback_data=available_groups[i + 1]))
    bot.send_message(callback.message.chat.id, "Выберите вашу группу", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in EDUCATION_DEGREES)
def callback_degree(callback: telebot.types.CallbackQuery):
    degree = callback.data
    chat_id = callback.message.chat.id
    bot.send_message(chat_id, f"Ваша получаемая степень образования - {degree}")
    us_id = callback.from_user.id
    User.update(education_degree=degree).where(User.user_id == us_id).execute()
    markup = telebot.types.InlineKeyboardMarkup()
    for name in EDUCATION_PROGRAMS_SHORT:
        markup.row(telebot.types.InlineKeyboardButton(text=str(name),
                                                      callback_data=str(name)))
    bot.send_message(chat_id, "Выберите ваше образовательное направление",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in INSTITUTE_FACULTIES)
def callback_faculty(callback: telebot.types.CallbackQuery):
    # получение информации о факультете пользователя
    faculty = callback.data
    bot.send_message(callback.message.chat.id, f"Ваш факультет - {faculty}")
    us_id = callback.from_user.id
    # обновление информации в базе данных
    query = User.update(user_faculty=faculty).where(User.user_id == us_id)
    query.execute()
    bot.send_message(callback.message.chat.id, "Выберите получаемую степень образования",
                     reply_markup=telebot.types.InlineKeyboardMarkup(). \
                     row(telebot.types.InlineKeyboardButton(text=EDUCATION_DEGREES[0],
                                                            callback_data=EDUCATION_DEGREES[0]),
                         telebot.types.InlineKeyboardButton(text=EDUCATION_DEGREES[1],
                                                            callback_data=EDUCATION_DEGREES[1])))


@bot.callback_query_handler(func=lambda call: call.data.isdigit() and len(call.data) == 4)
def callback_year(callback: telebot.types.CallbackQuery):
    # отправка ответного сообщения пользователю
    bot.send_message(callback.message.chat.id, f"Год вашего поступления на текущую "
                                               f"образовательную программу - {callback.data}")
    # получение информации о пользователе
    year = callback.data  # год поступления пользователя
    user_full_name = callback.from_user.full_name
    user_id = callback.from_user.id
    user_login = callback.from_user.username
    # сохранение в базу данных нового пользователя
    query = User.insert(user_id=user_id, user_full_name=user_full_name, user_login=user_login,
                        admission_year=year)
    query.execute()

    # отправка следующего сообщения, чтобы узнать факультет
    markup = telebot.types.InlineKeyboardMarkup()
    for i in range(0, len(INSTITUTE_FACULTIES), 2):
        elem1 = INSTITUTE_FACULTIES[i]
        if i + 1 == len(INSTITUTE_FACULTIES):
            markup.row(telebot.types.InlineKeyboardButton(text=elem1, callback_data=elem1))
        else:
            elem2 = INSTITUTE_FACULTIES[i + 1]
            markup.row(telebot.types.InlineKeyboardButton(text=elem1, callback_data=elem1),
                       telebot.types.InlineKeyboardButton(text=elem2, callback_data=elem2))
    bot.send_message(callback.message.chat.id,
                     "Выберите ваш факультет",
                     reply_markup=markup)


@bot.message_handler(commands=["start"])
def start_message(message: telebot.types.Message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=False)
    markup.row(telebot.types.KeyboardButton("На сегодня"),
               telebot.types.KeyboardButton("На завтра"))
    markup.row(telebot.types.KeyboardButton("На текущую неделю"),
               telebot.types.KeyboardButton("На следующую неделю"))
    bot.send_message(message.chat.id, "Бот начал работу", reply_markup=markup)


@bot.message_handler(commands=["choose_group"])
def choose_group_message(message: telebot.types.Message):
    flags_dict["choosing_group_flag"] = True
    markup = telebot.types.InlineKeyboardMarkup()
    for year in range(2020, 2024, 2):
        markup.row(telebot.types.InlineKeyboardButton(text=str(year), callback_data=str(year)),
                   telebot.types.InlineKeyboardButton(text=str(year + 1),
                                                      callback_data=str(year + 1)))
    bot.send_message(message.chat.id,
                     "Выберите год вашего поступления на текущее направление",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in SETTINGS_CALLBACKS)
def callback_from_settings(callback: telebot.types.CallbackQuery):
    text = callback.data
    us_id, mes_id = callback.from_user.id, callback.message.id
    url = list(elem.group_url for elem in User.select().where(User.user_id == us_id))[0]
    schedule = week_timetable_dict(url)
    duplicate_items: dict[str: dict[str: list[str]]] = dict()

    for key, value in schedule.items():
        k = key.split(", ")[0]
        duplicate_items[k] = dict()
        for i in range(len(value) - 1):
            if (i == 0 and value[i][0] == value[i + 1][0]) or \
                    (i > 0 and value[i][0] == value[i + 1][0] and value[i-1][0] != value[i][0]):
                # value[i][0] - время проведения
                if value[i][0] not in duplicate_items[k].keys():
                    duplicate_items[k][value[i][0]] = list()
                duplicate_items[k][value[i][0]].append(value[i])
                duplicate_items[k][value[i][0]].append(value[i + 1])
            elif i > 0 and value[i][0] == value[i + 1][0] and value[i-1][0] == value[i][0]:
                if value[i][0] not in duplicate_items[k].keys():
                    duplicate_items[k][value[i][0]] = list()
                duplicate_items[k][value[i][0]].append(value[i + 1])
    json.dump(duplicate_items, open(f"duplicate_items\{us_id}.json", "w"), indent=4)


# присылает в ответ сообщение с возможными настройками; добавлять их по мере роста функционала
@bot.message_handler(commands=["settings"])
def settings_message(message: telebot.types.Message):
    markup = telebot.types.InlineKeyboardMarkup()
    # выбор своей подгруппы в дублирующихся предметах
    markup.row(telebot.types.InlineKeyboardButton(text="Choosing subgroup",
                                                  callback_data="Choosing subgroup"))
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


def make_week_schedule(sched: dict[str, list]) -> str:
    output = "Расписание на неделю\n"
    for key, value in sched.items():
        output += f"<em>{key}</em>\n"
        for elem in value:
            if "practical class" in elem[1]:
                output += f"<b>{elem[1][:elem[1].index(' class')].strip()}</b> <u>{elem[0]}</u>\n"
            else:
                output += f"<b>{elem[1]}</b> <u>{elem[0]}</u>\n"
        output += "\n"
    return output


def make_one_day_schedule(sched: dict[str, list], day: str) -> str:
    output = ""
    key = list(sched.keys())[0] if len(
        list(k for k in sched.keys() if k.endswith(day))) == 0 else \
        list(k for k in sched.keys() if k.endswith(day))[0]
    if not key.endswith(day):
        output += "В указанный день нет занятий.\n"
    output += f"Расписание на <em>{key}</em>\n"
    for elem in sched[key]:
        subj_info, time_info = elem[1], elem[0]
        if "practical class" in subj_info:
            subj_info = subj_info[:subj_info.index(" class")].strip()
        output += f"<b>{subj_info}</b> <u>{time_info}</u>\n"
    return output


if __name__ == "__main__":
    bot.polling(none_stop=True)
