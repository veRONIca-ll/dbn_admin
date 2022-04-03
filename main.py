import os
import telebot
from dotenv import load_dotenv

load_dotenv()

MY_ENV_VAR = os.getenv('TELEBOT_TOKEN')
