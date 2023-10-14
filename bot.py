import telebot

bot = telebot.TeleBot(open("personal information.txt").readlines()[2].strip())
flags_dict: dict[str, bool] = dict()
flags_dict["choosing_group_flag"] = False


@bot.callback_query_handler(func=lambda call: call.data in ["2020", "2021", "2022", "2023"])
def callback_year(callback: telebot.types.CallbackQuery):
    bot.send_message(callback.message.chat.id, "ok")
    print("HERE")
    if callback.data == "2020":
        print("year 2020")
    else:
        print(callback.data)


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
    if flags_dict["choosing_group_flag"]:
        flags_dict["choosing_group_flag"] = False
        group_name = message.text


if __name__ == "__main__":
    bot.polling(none_stop=True)
