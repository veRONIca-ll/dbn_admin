import re
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ParseMode, KeyboardButton
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, RegexHandler
from db_operations import find_user, get_departments, add_user
from utils.helpers import send_list, split_into_fullname


def start(update: Update, context: CallbackContext):
    user = find_user(update.effective_chat.id)
    if user == None:
        button = [[KeyboardButton('Регистрация')]]
        context.bot.send_message(update.effective_chat.id, 'Вас приветсвует бот отдела ИТ-поддержки!')
        context.bot.send_message(update.effective_chat.id, 'Для того, чтобы я знал, как к Вам в дальнейшем обращаться, нажмите кнопку "Регистрация"',
            reply_markup=ReplyKeyboardMarkup(button))
    else:
        context.bot.send_message(update.effective_chat.id, f"Здравствуйте, {user['first_name']} {user['middle_name']}.")


def message_handler(update: Update, context: CallbackContext):
    if update.message.text == 'Регистрация':
        departments = get_departments()
        if departments != ():
            context.bot.send_message(update.effective_chat.id, 'Давайте знакомиться! Напишите свое ФИО, чтобы я знал, как к Вам обращаться, а также укажите номер отдела из предоставленного ниже списка.')
            context.bot.send_message(update.effective_chat.id, send_list(departments))
            context.bot.send_message(update.effective_chat.id, 'Пример ответа: Иванов Иван Иванович 3')
        else:
            context.bot.send_message(update.effective_chat.id, 'В данный момент список отделов обновляется, пожалуйста, пропутсите шаг регистрации.')
    if re.match('^[А-Я][а-я]*([-][А-Я][а-я]*)?\s[А-Я][а-я]*\s[А-Я][а-я]*\s\d$', update.message.text):
        data = split_into_fullname(update.effective_chat.id, update.message.text)
        if add_user(data):
            context.bot.send_message(
                update.effective_chat.id,
                f"Приятно познакомиться, {data['first_name']} {data['middle_name']}!",
                reply_markup = ReplyKeyboardMarkup([[KeyboardButton('Как пользоваться?')]]))
        else:
            context.bot.send_message(update.effective_chat.id, f"Возникла небольшая проблема, давайте познакомимся в другой раз!")
    if update.message.text == 'Как пользоваться?':
        help(update, context)

def help(update: Update, context: CallbackContext):
    # TODO: output for help info 
    context.bot.send_message(update.effective_chat.id, f"Здесь будет позже размещена инструкция по использованию бота, ждите!")



def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv('TELEBOT_TOKEN'))
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', start))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
