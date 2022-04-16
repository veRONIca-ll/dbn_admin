import re
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ParseMode, KeyboardButton
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler
from db_operations import find_user, get_departments, add_user, register_user
from helpers import send_list, split_into_fullname


def start(update: Update, context: CallbackContext):
    user = find_user(update.effective_chat.id)
    if user == tuple():
        context.bot.send_message(update.effective_chat.id, 'Возникли технические проблемы. Попробуйте позже!')
        return None

    if user == None:
        add_user(update.effective_chat.id, update.message.from_user.first_name)
        button = [[KeyboardButton('Регистрация сотрудника')],[KeyboardButton('Регистрация эксперта ИТ-отдела')]]
        context.bot.send_message(update.effective_chat.id, 'Вас приветсвует бот отдела ИТ-поддержки!')
        context.bot.send_message(update.effective_chat.id, 'Для того, чтобы я знал, как к Вам в дальнейшем обращаться, нажмите кнопку "Регистрация пользователя", если вы не являетесь экспетром ИТ-отдела, иначе нажмите "Регистарция эксперта ИТ-отдела',
            reply_markup=ReplyKeyboardMarkup(button))
    else:
        if user['first_name'] != None and user['second_name'] != None:
            context.bot.send_message(update.effective_chat.id, f"Здравствуйте, {user['first_name']} {user['middle_name']}.")
        else:
            context.bot.send_message(update.effective_chat.id, f"Здравствуйте, {user['nick']}.")


def message_handler(update: Update, context: CallbackContext):
    if update.message.text == 'Регистрация сотрудника':
        buttons = [[KeyboardButton('Ввести ФИО')],[KeyboardButton('Пропустить шаг ввода ФИО')]]
        context.bot.send_message(update.effective_chat.id, 'Регистрация состоит из двух шагов. Ввода ФИО и выбора направления отдела.',
            reply_markup=ReplyKeyboardMarkup(buttons))
    
    if update.message.text == 'Ввести ФИО':
        context.bot.send_message(update.effective_chat.id, 'Давайте знакомиться! Напишите свое ФИО, чтобы я знал, как к Вам обращаться.')
        context.bot.send_message(update.effective_chat.id, 'Пример ответа: Иванов Иван Иванович')
    
    if re.match('^[А-Я][а-я]*([-][А-Я][а-я]*)?\s[А-Я][а-я]*\s[А-Я][а-я]*$', update.message.text):
        print('FIO')
        data = split_into_fullname(update.effective_chat.id, update.message.text)
        if register_user(data):
            buttons = [[KeyboardButton('Выбрать направление отдела')], [KeyboardButton('Пропустить шаг выбора направление отдела')]]
            context.bot.send_message(update.effective_chat.id,
                f"Приятно познакомиться, {data['first_name']} {data['middle_name']}!\nТеперь давайте выберем направление Вашего отдела",
                reply_markup = ReplyKeyboardMarkup(buttons))
        else:
            context.bot.send_message(update.effective_chat.id, f"Возникла небольшая проблема, давайте познакомимся в другой раз!")
    
    if update.message.text == 'Пропустить шаг ввода ФИО':
        buttons = [[KeyboardButton('Выбрать направление отдела')], [KeyboardButton('Пропустить шаг выбора направление отдела')]]
        context.bot.send_message(update.effective_chat.id,
            f"Если Вы, передумаете, у Вас будет возможность заполнить этот шаг!\nТеперь давайте выберем направление Вашего отдела",
            reply_markup = ReplyKeyboardMarkup(buttons))
    
    # if update.message.text == 'Выбрать направление отдела':
    #     departments = get_departments()
    #     if departments != ():
    #         context.bot.send_message(update.effective_chat.id, 'Укажите номер Вашего направления отдела из предоставленного ниже списка.')
    #         context.bot.send_message(update.effective_chat.id, f'Направления:\n{send_list(departments)}')
    #         context.bot.send_message(update.effective_chat.id, 'Пример ответа: 3')
    #     else:
    #         context.bot.send_message(update.effective_chat.id, 
    #         'В данный момент список отделов обновляется, пожалуйста, пропутсите этот шаг регистрации.',
    #         reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Инструкция пользования')]]))
    
    if update.message.text == 'Пропустить шаг выбора направление отдела':
        context.bot.send_message(update.effective_chat.id,
            f"Если Вы передумаете, у Вас будет возможность заполнить этот шаг!",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Инструкция пользования')]]))
    
    if update.message.text == 'Инструкция пользования':
        help(update, context)

def help(update: Update, context: CallbackContext):
    # TODO: output for help info 
    context.bot.send_message(update.effective_chat.id, f"Здесь будет позже размещена инструкция по использованию бота, ждите!")

def choose_direction(update: Update, context: CallbackContext):
    departments = get_departments()
    if departments != ():
        context.bot.send_message(update.effective_chat.id, 'Укажите номер Вашего направления отдела из предоставленного ниже списка.')
        context.bot.send_message(update.effective_chat.id, f'Направления:\n{send_list(departments)}')
        context.bot.send_message(update.effective_chat.id, 'Пример ответа: 3')
    else:
        context.bot.send_message(update.effective_chat.id, 
        'В данный момент список отделов обновляется, пожалуйста, пропутсите этот шаг регистрации.',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Инструкция пользования')]]))
    return 0

def save_direction(update: Update, context: CallbackContext):
    context.bot.send_message(update.effective_chat.id, 
        'OK',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Инструкция пользования')]]))

    
def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv('TELEBOT_TOKEN'))
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Выбрать направление отдела'), choose_direction)],
        fallbacks=[],
        states={
            0: [MessageHandler(Filters.regex('\d{1}'), save_direction)],
        },
    ))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
