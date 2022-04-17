# import os
# import telebot
# from dotenv import load_dotenv

# load_dotenv()

# MY_ENV_VAR = os.getenv('TELEBOT_TOKEN')
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, 
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler)


FIRST, SECOND = range(2)

counter = 0

keyboard = [[InlineKeyboardButton('Decrement', callback_data='0')],
            [InlineKeyboardButton(f'[{counter}]', callback_data='1')],
            [InlineKeyboardButton('Increment', callback_data='2')]]


def start(update, context):
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Please choose one of our services\n',
        reply_markup=reply_markup
    )

    return FIRST


def update_and_get_reply_markup(inc_or_dec=None):
    global keyboard
    global counter
    if inc_or_dec == True:
        counter += 1
    else:
        counter -= 1

    keyboard[1][0] = InlineKeyboardButton(
        f'[{counter}]', callback_data='2')

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


def increment(update, context):
    query = update.callback_query

    reply_markup = update_and_get_reply_markup(inc_or_dec=True)
    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Please choose one of our services\n",
        reply_markup=reply_markup
    )

    return FIRST


def decrement(update, context):
    query = update.callback_query

    reply_markup = update_and_get_reply_markup()
    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Please choose one of our services\n",
        reply_markup=reply_markup
    )

    return FIRST


def main():
    updater = Updater(
        '1028158602:AAHNqITbhGdCTFye0dtqOaCuF-G06nzKpks', use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [CallbackQueryHandler(decrement, pattern='^'+str(0)+'$'),
                    CallbackQueryHandler(increment, pattern='^'+str(2)+'$')]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
