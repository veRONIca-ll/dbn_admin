import telebot
import os

def login():
    try:
        bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
        return bot
    except Exception:
        return "Telegram Error"
