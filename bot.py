import telebot

bot = telebot.TeleBot(open("personal information.txt").readline().strip())
choosing_group_flag = False


@bot.message_handler(commands=["start"])
def main(message: telebot.types.Message):
    bot.send_message(message.chat.id, "Бот начал работу")


@bot.message_handler(commands=["choose_group"])
def choose_group_message(message: telebot.types.Message):
    bot.send_message(message.chat.id, "Введите название вашей группы")
    global choosing_group_flag
    choosing_group_flag = True


@bot.message_handler()
def take_message(message: telebot.types.Message):
    global choosing_group_flag
    user_full_name = message.from_user.full_name
    user_id = message.from_user.id
    user_login = message.from_user.username
    if choosing_group_flag:
        choosing_group_flag = False
        group_name = message.text



if __name__ == "__main__":
    bot.polling(none_stop=True)
