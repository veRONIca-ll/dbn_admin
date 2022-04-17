import os
import sys
# sys.path is a list of absolute path strings
sys.path.append(os.getenv('PATH_TO_APP_FOLDER'))
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ParseMode, KeyboardButton
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler
from db.db_operations import find_user, get_departments, add_user, add_fio, add_department
from utils.helpers import send_list, split_into_fullname
STEP_FIO, SAVE_FIO, STEP_DEPS, SAVE_DEPS, FINISH = range(5)

def start(update: Update, context: CallbackContext):
    ''' Приветствие пользователя или запрос на регистрацию '''
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
    if update.message.text == 'Инструкция пользования':
        help(update, context)

def help(update: Update, context: CallbackContext):
    # TODO: output for help info 
    context.bot.send_message(update.effective_chat.id, f"Здесь будет позже размещена инструкция по использованию бота, ждите!")

def register(update:Update, context: CallbackContext):
    ''' Начало и описание процесса регистрации '''
    buttons = [[KeyboardButton('Ввести ФИО')],[KeyboardButton('Пропустить шаг ввода ФИО')]]
    context.bot.send_message(update.effective_chat.id, 'Регистрация состоит из двух шагов. Ввода ФИО и выбора направления отдела. Вы можете пропускать шаги регистарции, но это не рекомендуется.',
        reply_markup=ReplyKeyboardMarkup(buttons))
    return STEP_FIO

def get_fio(update:Update, context: CallbackContext):
    ''' Запрос на получение корректно введенного ФИО '''
    context.bot.send_message(update.effective_chat.id, 'Давайте знакомиться! Напишите свое ФИО, чтобы я знал, как к Вам обращаться.')
    context.bot.send_message(update.effective_chat.id, 'Пример ответа: Иванов Иван Иванович')
    return SAVE_FIO

def set_fio(update:Update, context: CallbackContext):
    ''' Запись ФИО пользователя '''
    data = split_into_fullname(update.effective_chat.id, update.message.text, False)
    if not add_fio(data):
        buttons = [[KeyboardButton('Ввести ФИО')],[KeyboardButton('Пропустить шаг ввода ФИО')]]
        context.bot.send_message(
            update.effective_chat.id,
            "Возникла небольшая проблема. Попробуйте еще раз или пропустите шаг.",
            reply_markup = ReplyKeyboardMarkup(buttons)
        )
        
        return STEP_FIO
    buttons = [[KeyboardButton('Выбрать направление отдела')], [KeyboardButton('Пропустить шаг выбора направление отдела')]]
    context.bot.send_message(
        update.effective_chat.id,
        f"Приятно познакомиться, {data['first_name']} {data['middle_name']}!\nТеперь давайте выберем направление Вашего отдела",
        reply_markup = ReplyKeyboardMarkup(buttons)
    )
    
    return STEP_DEPS

def set_admin_fio(update:Update, context: CallbackContext):
    ''' Запись ФИО эксперта ИТ-отдела '''
    data = split_into_fullname(update.effective_chat.id, update.message.text, True)
    if not add_fio(data):
        buttons = [[KeyboardButton('Ввести ФИО')],[KeyboardButton('Пропустить шаг ввода ФИО')]]
        context.bot.send_message(
            update.effective_chat.id,
            "Возникла небольшая проблема. Попробуйте еще раз или пропустите шаг.",
            reply_markup = ReplyKeyboardMarkup(buttons)
        )
        
        return STEP_FIO
    context.bot.send_message(
        update.effective_chat.id,
        f"Приятно познакомиться, {data['first_name']} {data['middle_name']}!",
        reply_markup = ReplyKeyboardRemove()
    )

def skip_fio(update:Update, context: CallbackContext):
    ''' Пропуск шага ввода ФИО для пользователя '''
    buttons = [[KeyboardButton('Выбрать направление отдела')], [KeyboardButton('Пропустить шаг выбора направление отдела')]]
    context.bot.send_message(update.effective_chat.id,
        f"Если Вы, передумаете, у Вас будет возможность заполнить этот шаг!\nТеперь давайте выберем направление Вашего отдела",
        reply_markup = ReplyKeyboardMarkup(buttons))

    return STEP_DEPS

def skip_admin_fio(update:Update, context: CallbackContext):
    ''' Пропуск шага ввода ФИО для эксперта ИТ-отдела '''
    context.bot.send_message(update.effective_chat.id,
        f"Если Вы, передумаете, у Вас будет возможность заполнить этот шаг!",
        reply_markup = ReplyKeyboardRemove())

def get_department(update:Update, context: CallbackContext):
    ''' Вывод всех направлений отделений для пользователя '''
    departments = get_departments()
    if departments != ():
        context.bot.send_message(update.effective_chat.id, 'Укажите номер Вашего направления отдела из предоставленного ниже списка.')
        context.bot.send_message(update.effective_chat.id, f'Направления:\n{send_list(departments)}')
        context.bot.send_message(update.effective_chat.id, 'Пример ответа: 3')
    else:
        context.bot.send_message(update.effective_chat.id, 
        'В данный момент список отделов обновляется, пожалуйста, пропутсите этот шаг регистрации.',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Инструкция пользования')]]))
    return SAVE_DEPS

def set_department(update:Update, context: CallbackContext):
    ''' Установление номера направления отделений для пользователя '''
    if not add_department(update.effective_chat.id, update.message.text):
        buttons = [[KeyboardButton('Выбрать направление отдела')], [KeyboardButton('Пропустить шаг выбора направление отдела')]]
        context.bot.send_message(
            update.effective_chat.id,
            f"Возникла небольшая проблема: был введен некорректный номер отдела. Попробуйте еще раз или пропустите шаг.",
            reply_markup = ReplyKeyboardMarkup(buttons)
        )
        return STEP_DEPS
    
    context.bot.send_message(update.effective_chat.id,
        f"Направление Вашего отдела было записано",
        reply_markup = ReplyKeyboardRemove())
        
def skip_department(update:Update, context: CallbackContext):
    ''' Пропуск шага выбора направления отделений для пользователя '''
    context.bot.send_message(update.effective_chat.id,
            f"Если Вы передумаете, у Вас будет возможность заполнить этот шаг!",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Инструкция пользования')]]))

def incorrect_name_input(update:Update, context: CallbackContext):
    ''' Сообщение о неправильном вводе ФИО '''
    context.bot.send_message('Пожалуйста, введите свое ФИО так, как указано в примере.')

def incorrect_department_input(update:Update, context: CallbackContext):
    ''' Сообщение о неправильном вводе номера направления '''
    context.bot.send_message('Пожалуйста, введите номер своего направления отделения так, как указано в примере.')

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
        entry_points=[MessageHandler(Filters.regex('Регистрация сотрудника'), register)],
        fallbacks=[],
        states={
            STEP_FIO: [
                    MessageHandler(Filters.regex('Ввести ФИО'), get_fio),
                    MessageHandler(Filters.regex('Пропустить шаг ввода ФИО'), skip_fio),
                    MessageHandler(Filters.text, incorrect_name_input)
                ],
            SAVE_FIO: [MessageHandler(Filters.regex('^[А-Я][а-я]*([-][А-Я][а-я]*)?\s[А-Я][а-я]*\s[А-Я][а-я]*$'), set_fio)],
            STEP_DEPS: [
                    MessageHandler(Filters.regex('Выбрать направление отдела'), get_department),
                    MessageHandler(Filters.regex('Пропустить шаг выбора направление отдела'), skip_department),
                    MessageHandler(Filters.text, incorrect_department_input),
                ],
            SAVE_DEPS: [MessageHandler(Filters.regex('\d'), set_department)]
        },
    ))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Регистрация эксперта ИТ-отдела'), register)],
        fallbacks=[],
        states={
            STEP_FIO: [
                    MessageHandler(Filters.regex('Ввести ФИО'), get_fio),
                    MessageHandler(Filters.regex('Пропустить шаг ввода ФИО'), skip_admin_fio),
                    MessageHandler(Filters.text, incorrect_name_input),
                ],
            SAVE_FIO: [MessageHandler(Filters.regex('^[А-Я][а-я]*([-][А-Я][а-я]*)?\s[А-Я][а-я]*\s[А-Я][а-я]*$'), set_admin_fio)],
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
