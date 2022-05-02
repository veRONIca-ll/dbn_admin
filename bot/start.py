
from operator import concat
import os
import sys
# sys.path is a list of absolute path strings
sys.path.append(os.getenv('PATH_TO_APP_FOLDER'))

from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from db.db_operations import find_user, get_departments, add_user, add_fio, add_department, get_categories
from utils.helpers import send_list, split_into_fullname, pretty_output
from elasticsearch_integration.search import search_es
from telegram_bot_pagination import InlineKeyboardPaginator

STEP_FIO, SAVE_FIO, STEP_DEPS, SAVE_DEPS, FINISH = range(5)
AKS_CATEGORY, ASK_DESCRIPTION, SEARCH_SOLUTIONS, ASK_FOR_HELP = range(4)
user_info = {}
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
        button = [[KeyboardButton('Оставить заявку')]]
        if user['first_name'] != None and user['second_name'] != None:
            context.bot.send_message(update.effective_chat.id, f"Здравствуйте, {user['first_name']} {user['middle_name']}.",
                reply_markup = ReplyKeyboardMarkup(button))
        else:
            context.bot.send_message(update.effective_chat.id, f"Здравствуйте, {user['nick']}.",
                reply_markup = ReplyKeyboardMarkup(button))


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
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Инструкция пользования')], [KeyboardButton('Оставить заявку')]]))
    return ConversationHandler.END

def incorrect_name_input(update: Update, context: CallbackContext):
    ''' Сообщение о неправильном вводе ФИО '''
    context.bot.send_message(update.effective_chat.id, 'Пожалуйста, введите свое ФИО так, как указано в примере.')

def incorrect_department_input(update:Update, context: CallbackContext):
    ''' Сообщение о неправильном вводе номера направления '''
    context.bot.send_message(update.effective_chat.id, 'Пожалуйста, введите номер своего направления отделения так, как указано в примере.')

def get_category_problem(update: Update, context: CallbackContext):
    ''' Уточнение категории, к которой относится заявка '''
    categories = get_categories()
    print(type(categories))
    keyboard = []

    for value in categories.items():
        print(value)
        keyboard.append([InlineKeyboardButton(text=value[1], callback_data=value[0])])
    
    context.bot.send_message(update.effective_chat.id, 'Выберите категорию Вашей проблемы:', reply_markup=InlineKeyboardMarkup(keyboard))
    return ASK_DESCRIPTION



def get_description_problem(update: Update, context: CallbackContext):
    print('in')
    global user_info
    query = update.callback_query
    print(query.data)
    user_info[update.effective_chat.id] = query.data
    context.bot.send_message(update.effective_chat.id, 'Кратко опишите свою проблему')
    context.bot.send_message(update.effective_chat.id, 'Например, не включается принтер')
    return SEARCH_SOLUTIONS

def find_solution(update: Update, context: CallbackContext):
    global user_info
    category_id = user_info[update.effective_chat.id]
    print(category_id)
    context.bot.send_message(update.effective_chat.id, 'Поиск решения данной проблемы начался...')
    # print(update.message.text)
    
    response = search_es(category_id, update.message.text)
    if response == []:
        context.bot.send_message(update.effective_chat.id, 'Ничего не найдено по Вашему запросу')
        # TODO : create task in Jira + send messages to admins
        unsuccess_reply(update, context)
    else:
        context.bot.send_message(update.effective_chat.id, 'Вот, что удалось найти по Вашему запросу:')
        context.bot.send_message(update.effective_chat.id, pretty_output(response))
        context.bot.send_message(update.effective_chat.id, 'Вам помогли результаты поиска?',
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Да, помогли')], [KeyboardButton('Нет, не помогли')]])
        )

def success_reply(update: Update, context: CallbackContext):
    print('i am in')
    context.bot.send_message(update.effective_chat.id,
        'Рады были помочь! Если возникнут проблемы, оставляйте заявку снова. Хорошего дня!',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('/start')]]))
    return ConversationHandler.END

def unsuccess_reply(update: Update, context: CallbackContext):
    # TODO : create task in Jira + send messages to admins
    print(update.message.text)
    context.bot.send_message(update.effective_chat.id,
        'Сейчас создается заявка, которую будут решать эксперты отдела')
    return ConversationHandler.END

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
        }
    ))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Оставить заявку'), get_category_problem)],
        fallbacks=[],
        states={
            ASK_DESCRIPTION: [CallbackQueryHandler(get_description_problem)],
            SEARCH_SOLUTIONS: [
                    MessageHandler(Filters.regex('Да, помогли'), success_reply),
                    MessageHandler(Filters.regex('Нет, не помогли'), unsuccess_reply),
                    MessageHandler(Filters.text, find_solution),
                ]
        },
    ))

    # dispatcher.add_handler(CallbackQueryHandler(Filters.text, message_handler))
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
