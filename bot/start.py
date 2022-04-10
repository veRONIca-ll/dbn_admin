
import telebot
import re
import os
from telegram import ReplyKeyboardMarkup, Update, ParseMode, KeyboardButton
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, RegexHandler
from __init__ import login
from db_operations import find_user, get_departments, add_user
from helpers import send_list

bot = login()
if bot == 'Telegram Error':
    print('Failed to connect')

def start(update: Update, context: CallbackContext):
    print(update.effective_chat.id)
    user = find_user(update.effective_chat.id)
    if user == None:
        button = [[KeyboardButton('Регистрация')]]
        context.bot.send_message(update.effective_chat.id, 'Вас приветсвует бот отдела ИТ-поддержки!')
        context.bot.send_message(update.effective_chat.id, 'Для того, чтобы я знал, как к Вам в дальнейшем обращаться, нажмите кнопку "Регистрация"',
            reply_markup=ReplyKeyboardMarkup(button))
    else:
        bot.send_message(update.effective_chat.id, f"Здравствуйте, {user['first_name']} {user['middle_name']}.")


def message_handler(update: Update, context: CallbackContext):
    if update.message.text == 'Регистрация':
        departments = get_departments()
        if departments:
            context.bot.send_message(update.effective_chat.id, 'Давайте знакомиться! Напишите свое ФИО, чтобы я знал, как к Вам обращаться, а также укажите номер отдела из предоставленного ниже списка.')
            context.bot.send_message(update.effective_chat.id, send_list(departments))
            context.bot.send_message(update.effective_chat.id, 'Пример ответа: Иванов Иван Иванович 3')
    if re.match('^[А-Я][а-я]*([-][А-Я][а-я]*)?\s[А-Я][а-я]*\s[А-Я][а-я]*\s\d$', update.message.text):
        register(update.effective_chat.id, update.message.text)

# def help():


def register(id, message):
    # insert into the table and return FIO
    data = message.split()
    add_user((id, data[1], data[0], data[2], data[3]))



def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv('TELEBOT_TOKEN'))
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    # dispatcher.add_handler(RegexHandler('^[А-Я][а-я]*([-][А-Я][а-я]*)?\s[А-Я][а-я]*\s[А-Я][а-я]*\s\d$', register))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
