import telebot
import peewee as pw
from models import User


db = pw.SqliteDatabase("db.sqlite3")
bot = telebot.TeleBot(open("personal information.txt").readlines()[2].strip())
flags_dict: dict[str, bool] = dict()
flags_dict["choosing_group_flag"] = False
INSTITUTE_FACULTIES = ["Мат-мех"]

# выполнять каждый раз при тестировании и создании бота
#db.drop_tables([User])
#db.create_tables([User])
#print("done")


@bot.callback_query_handler(func=lambda call: call.data.isdigit() and len(call.data) == 4)
def callback_year(callback: telebot.types.CallbackQuery):
    # отправка ответного сообщения пользователю
    bot.send_message(callback.message.chat.id, f"Год вашего поступления на текущую "
                                               f"образовательныу программу - {callback.data}")
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
