import os
import sys
from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
sys.path.append(os.getenv('PATH_TO_APP_FOLDER'))

from job.sync import sync
from db.db_operations import get_user, get_departments, add_user, update_user_fio, update_user_department, get_categories, get_admins_id, update_user_admin
from integrations.es_integration import search_es
from integrations.trello_integration import create_card
from utils.helpers import send_list, split_into_fullname, pretty_output

# Константы переходов
STEP_FIO, SAVE_FIO, STEP_DEPS, SAVE_DEPS = range(4)
STEP_ADMIN_FIO, SAVE_ADMIN_FIO = range(2)
AKS_CATEGORY, ASK_DESCRIPTION, SEARCH_SOLUTIONS = range(4)
#
user_info = {}



# Приветствие
def start(update: Update, context: CallbackContext):
    ''' Приветствие пользователя или запрос на регистрацию '''
    user = get_user(update.effective_chat.id)
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
        admin_button = [[KeyboardButton('Информация по Боту')],[KeyboardButton('Инструкция по обработке заявки')], [KeyboardButton('Изменение ФИО')]]
        if user['first_name'] != None and user['second_name'] != None:
            context.bot.send_message(update.effective_chat.id, f"Здравствуйте, {user['first_name']} {user['middle_name']}.",
                reply_markup = ReplyKeyboardMarkup(admin_button) if user['admin'] else ReplyKeyboardMarkup(button))
        else:
            context.bot.send_message(update.effective_chat.id, f"Здравствуйте, {user['nick']}.",
                reply_markup = ReplyKeyboardMarkup(admin_button) if user['admin'] else ReplyKeyboardMarkup(button))



# Информационные сообщения
def help(update: Update, context: CallbackContext):
    ''' Вывод информации для пользователя '''
    context.bot.send_message(update.effective_chat.id,
        f"<b>Инструкция пользования бота:</b>\nЗдесь Вы можете оставлять заявки по Вашей проблеме.\nБот будет стараться подобрать решения для Ваше проблемы, если они не пойдойдут или их не будет, Ваша заявка будет отправлена экспертам ИТ-отдела.",
        parse_mode='HTML')

def info_admin(update: Update, context: CallbackContext):
    ''' Информация для экспертов '''
    context.bot.send_message(update.effective_chat.id,
     "<b>Инструкция для эксперта:</b>\n\nВ этот диалог будут приходить уведомления о заявках пользователей, которые не могут быть обработаны автоматически.\n\nВ уведомлении будет прикреплена ссылка на карточку в Trello, а также ссылка на диалог с пользователем, чтобы Вам было удобнее с ним связаться для обсуждения деталей. Успехов!",
     parse_mode='HTML')

def info_trello(update: Update, context: CallbackContext):
    ''' Инструкция для экспертов '''
    context.bot.send_message(update.effective_chat.id,
    "<b>Инструкция по работе с Trello карточкой:</b>\nВам придет уведомление о заявке, оставленной пользователем, с ссылкой на карточку Trello.",
        parse_mode='HTML')
    context.bot.send_message(update.effective_chat.id, 
        "<b>Шаги выполнения:</b>\n\n1)Если Вы решили взять эту заявку в обработку, необходимо сразу перенести карточку в список 'Doing'. \n\n<b><i>Если в данный момент у Вас в приоритете есть другие задачи, тогда Вам делать ничего не нужно.</i></b>\n\n2) После того как Вы решили проблему пользователя, Вам необходимо отписать шаги решения проблемы в описании карточки в формате: \n\n\t1) ...\n\t2) ...\n\t\t...\n\n3) Перенесите карточку в список 'Done', так отписанные Вами шаги решения проблемы запишутся в базу данных для автоматической обработки заявки",
        parse_mode='HTML')



# Регистрация пользователя
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
    data = split_into_fullname(update.effective_chat.id, update.message.text)
    if not update_user_fio(data):
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

def skip_fio(update:Update, context: CallbackContext):
    ''' Пропуск шага ввода ФИО для пользователя '''
    buttons = [[KeyboardButton('Выбрать направление отдела')], [KeyboardButton('Пропустить шаг выбора направление отдела')]]
    context.bot.send_message(update.effective_chat.id,
        f"Если Вы, передумаете, у Вас будет возможность заполнить этот шаг!\nТеперь давайте выберем направление Вашего отдела.",
        reply_markup = ReplyKeyboardMarkup(buttons))

    return STEP_DEPS

def get_department(update: Update, context: CallbackContext):
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

def set_department(update: Update, context: CallbackContext):
    ''' Установление номера направления отделений для пользователя '''
    if not update_user_department(update.effective_chat.id, update.message.text):
        buttons = [[KeyboardButton('Выбрать направление отдела')], [KeyboardButton('Пропустить шаг выбора направление отдела')]]
        context.bot.send_message(
            update.effective_chat.id,
            f"Возникла небольшая проблема: был введен некорректный номер отдела. Попробуйте еще раз или пропустите шаг.",
            reply_markup = ReplyKeyboardMarkup(buttons)
        )
        return STEP_DEPS
    else:
        context.bot.send_message(update.effective_chat.id,
            f"Направление Вашего отдела было записано, давайте начнем!",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Инструкция пользования')], [KeyboardButton('Оставить заявку')]]))
        return ConversationHandler.END
        
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



# Регистрация эксперта
def register_admin(update:Update, context: CallbackContext):
    ''' Начало и описание процесса регистрации '''
    buttons = [[KeyboardButton('Ввести ФИО')],[KeyboardButton('Пропустить шаг ввода ФИО')]]
    update_user_admin(update.effective_chat.id)
    context.bot.send_message(update.effective_chat.id, 'Регистрация состоит из одного шага - ввода ФИО. Вы можете пропускать шаг регистарции, но это не рекомендуется.',
        reply_markup=ReplyKeyboardMarkup(buttons))
    return STEP_ADMIN_FIO

def get_admin_fio(update:Update, context: CallbackContext):
    ''' Запрос на получение корректно введенного ФИО '''
    context.bot.send_message(update.effective_chat.id, 'Давайте знакомиться! Напишите свое ФИО, чтобы я знал, как к Вам обращаться.')
    context.bot.send_message(update.effective_chat.id, 'Пример ответа: Иванов Иван Иванович')
    return SAVE_ADMIN_FIO

def set_admin_fio(update:Update, context: CallbackContext):
    ''' Запись ФИО эксперта ИТ-отдела '''
    data = split_into_fullname(update.effective_chat.id, update.message.text)
    if not update_user_fio(data):
        buttons = [[KeyboardButton('Ввести ФИО')],[KeyboardButton('Пропустить шаг ввода ФИО')]]
        context.bot.send_message(
            update.effective_chat.id,
            "Возникла небольшая проблема. Попробуйте еще раз или пропустите шаг.",
            reply_markup = ReplyKeyboardMarkup(buttons)
        )
        
        return STEP_ADMIN_FIO
    context.bot.send_message(
        update.effective_chat.id,
        f"Приятно познакомиться, {data['first_name']} {data['middle_name']}!",
        reply_markup = ReplyKeyboardMarkup([[KeyboardButton('Информация по Боту')],[KeyboardButton('Инструкция по обработке заявки')], [KeyboardButton('Изменение ФИО')]])
    )

def skip_admin_fio(update: Update, context: CallbackContext):
    ''' Пропуск шага ввода ФИО для эксперта ИТ-отдела '''
    context.bot.send_message(update.effective_chat.id,
        f"Если Вы, передумаете, у Вас будет возможность заполнить этот шаг!",
        reply_markup = ReplyKeyboardMarkup([[KeyboardButton('Информация по Боту')],[KeyboardButton('Инструкция по обработке заявки')], [KeyboardButton('Изменение ФИО')]]))

    return ConversationHandler.END




# Обработка заявки
def get_category_problem(update: Update, context: CallbackContext):
    ''' Уточнение категории, к которой относится заявка '''
    categories = get_categories()
    keyboard = []
    for value in categories.items():
        keyboard.append([InlineKeyboardButton(text=value[1], callback_data=value[0])])
        context.bot.send_message(update.effective_chat.id, 'Выберите категорию Вашей проблемы:', reply_markup=InlineKeyboardMarkup(keyboard))
    return ASK_DESCRIPTION

def get_description_problem(update: Update, context: CallbackContext):
    ''' Запрос на описание проблемы пользователя '''
    global user_info
    query = update.callback_query
    user_info[update.effective_chat.id] = query.data
    context.bot.send_message(update.effective_chat.id, 'Кратко опишите свою проблему. Например:')
    context.bot.send_message(update.effective_chat.id, 'не могу распечатать документы на принтере')
    return SEARCH_SOLUTIONS

def find_solution(update: Update, context: CallbackContext):
    ''' Начало процесса обработки заявки '''
    global user_info
    category_id = user_info[update.effective_chat.id]
    print(category_id)
    context.bot.send_message(update.effective_chat.id, 'Поиск решения данной проблемы начался...')
    
    response = search_es(category_id, update.message.text)
    if response == []:
        context.bot.send_message(update.effective_chat.id, 'Ничего не найдено по Вашему запросу')
        unsuccess_reply(update, context)
        return ConversationHandler.END
    else:
        context.bot.send_message(update.effective_chat.id, 'Вот, что удалось найти по Вашему запросу:')
        context.bot.send_message(update.effective_chat.id, pretty_output(response), parse_mode='HTML')
        context.bot.send_message(update.effective_chat.id, 'Вам помогли результаты поиска?',
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Да, помогли')], [KeyboardButton('Нет, не помогли')]])
        )

def success_reply(update: Update, context: CallbackContext):
    ''' Успешная автоматическая обработка заявки '''
    context.bot.send_message(update.effective_chat.id,
        'Рады были помочь! Если возникнут проблемы, оставляйте заявку снова. Хорошего дня!',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('/start')]]))
    return ConversationHandler.END

def unsuccess_reply(update: Update, context: CallbackContext):
    ''' Создание задачи для обработки заявки '''
    global user_info
    context.bot.send_message(update.effective_chat.id,
        'Сейчас создается заявка, которую будут решать эксперты отдела...')
    card_url = create_card(update.effective_chat.id, user_info[update.effective_chat.id], update.message.text)
    if card_url != '':
        context.bot.send_message(update.effective_chat.id,
        'Заявка создана и уже рассматривается экспертами - ожидайте.')
        mailing_list_admin(card_url, update.effective_chat.id, context)
    else:
        context.bot.send_message(update.effective_chat.id,
        'Возникли проблемы с сервером, пожалуйста, обратиетсь в ИТ-отдел напрямую.',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('/start')]]))
    return ConversationHandler.END

def mailing_list_admin(url: str, user_id: int, context: CallbackContext):
    ''' Рассылка экспертам о новой заявке '''
    admins = get_admins_id()
    for admin in admins:
        context.bot.send_message(admin[0],
        f'<b>Поступила новая заявка: </b>\n {url}\n\n <a href="tg://user?id={user_id}">Вы можете связать с пользователем</a>', parse_mode='HTML')




def main() -> None:
    ''' Заупск бота '''
    updater = Updater(os.getenv('TELEBOT_TOKEN'))
    dispatcher = updater.dispatcher

    # Регистрация комманд
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
        entry_points=[
                MessageHandler(Filters.regex('Регистрация эксперта ИТ-отдела'), register_admin),
                MessageHandler(Filters.regex('Изменение ФИО'), register_admin),
            ],
        fallbacks=[],
        states={
            STEP_ADMIN_FIO: [
                    MessageHandler(Filters.regex('Ввести ФИО'), get_admin_fio),
                    MessageHandler(Filters.regex('Пропустить шаг ввода ФИО'), skip_admin_fio),
                    MessageHandler(Filters.text, incorrect_name_input),
                ],
            SAVE_ADMIN_FIO: [MessageHandler(Filters.regex('^[А-Я][а-я]*([-][А-Я][а-я]*)?\s[А-Я][а-я]*\s[А-Я][а-я]*$'), set_admin_fio)],
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

    dispatcher.add_handler(MessageHandler(Filters.regex('Информация по Боту'), info_admin))
    dispatcher.add_handler(MessageHandler(Filters.regex('Инструкция по обработке заявки'), info_trello))
    dispatcher.add_handler(MessageHandler(Filters.regex('Инструкция пользования'), help))
    
    # Старт бота
    updater.start_polling()

    # Джобы для синхронизации c Trello и переиндексации
    job = updater.job_queue
    job.run_once(sync, os.getenv('PERIOD_TIME'))

    updater.idle()

   
if __name__ == '__main__':
    main()
    
