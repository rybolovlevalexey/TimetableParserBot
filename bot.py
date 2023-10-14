import telebot
import peewee as pw
from models import User, EducationalDirection, GroupDirection

db = pw.SqliteDatabase("db.sqlite3")
bot = telebot.TeleBot(open("personal information.txt").readlines()[2].strip())
flags_dict: dict[str, bool] = dict()
flags_dict["choosing_group_flag"] = False
INSTITUTE_FACULTIES = ["Мат-мех"]
EDUCATION_DEGREES = ["Бакалавриат", "Магистратура"]
EDUCATION_PROGRAMS = sorted(set(elem.name for elem in EducationalDirection.select()))
EDUCATION_PROGRAMS_SHORT = list(map(lambda x: x[:60], EDUCATION_PROGRAMS))


# выполнять каждый раз при тестировании и создании бота
db.drop_tables([User])
db.create_tables([User])
print("done")


@bot.callback_query_handler(func=lambda call: call.data in EDUCATION_PROGRAMS_SHORT)
def callback_program(callback: telebot.types.CallbackQuery):
    program = callback.data
    bot.send_message(callback.message.chat.id, f"Ваше направление образования - {program}")
    us_id = callback.from_user.id
    User.update(education_program=program).where(User.user_id == us_id).execute()
    program_name = list(elem for elem in EDUCATION_PROGRAMS if str(elem).startswith(program))[0]
    available_groups = list(elem for elem in GroupDirection.select(GroupDirection.group_name).where(
        GroupDirection.educational_program_id == EducationalDirection.select(
            EducationalDirection.id).where(EducationalDirection.name == program_name and EducationalDirection.year == User.select(User.admission_year).where(User.user_id == us_id))))
    print(available_groups)


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
def main(message: telebot.types.Message):
    bot.send_message(message.chat.id, "Бот начал работу")


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


@bot.message_handler()
def take_message(message: telebot.types.Message):
    user_full_name = message.from_user.full_name
    user_id = message.from_user.id
    user_login = message.from_user.username
    print(user_full_name, user_id, user_login)
    if flags_dict["choosing_group_flag"]:
        flags_dict["choosing_group_flag"] = False
        group_name = message.text


if __name__ == "__main__":
    bot.polling(none_stop=True)
