# config.py - EXACT COPY OF CONSTANTS FROM ORIGINAL FILE
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ChatPermissions  # Update → Represents an incoming update from Telegram, like a message or command.
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext # ContextTypes → Provides the context for the message or chat, like info about who sent it, what chat it came from, etc.
from telegram.ext import MessageHandler, filters, CallbackQueryHandler
from telegram.ext import ChatMemberHandler
import logging
from telegram import ReplyKeyboardRemove, WebAppInfo
from telegram import ChatMember
import asyncio
import zipfile
from telegram import InputFile
import shutil
import glob
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import ApplicationHandlerStop
import os
from telegram import InputFile, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import MenuButtonWebApp, WebAppInfo


RICE_FOLDER = r"C:\Users\Admin\Music\async_Telegram_restaurant\FOLDERS\rice_folder"
SPICED_CHICKEN_FOLDER = r"C:\Users\Admin\Music\async_Telegram_restaurant\FOLDERS\spiced_fried_chicken"
FLAMED_GRILLED_CHICKEN = r"C:\Users\Admin\Music\async_Telegram_restaurant\FOLDERS\Flamed_grilled_chicken"
BURGER_AND_SNACK_FOLDER = r"C:\Users\Admin\Music\async_Telegram_restaurant\FOLDERS\Burger_folder"
BEVERAGES_FOLDER = r"C:\Users\Admin\Music\async_Telegram_restaurant\FOLDERS\Beverages"
ROTISSERIE_CHICKEN_FOLDER = r"C:\Users\Admin\Music\async_Telegram_restaurant\FOLDERS\Rotisserie_chicken_folder"
TASTY_SIDES = r"C:\Users\Admin\Music\async_Telegram_restaurant\FOLDERS\Tasty_sides"

MEAL_FOLDERS = {
    "rice": RICE_FOLDER,
    "spiced_chicken": SPICED_CHICKEN_FOLDER,
    "flamed_grilled_chicken": FLAMED_GRILLED_CHICKEN,
    "burgers_wraps_chickwizz": BURGER_AND_SNACK_FOLDER,
    "beverages": BEVERAGES_FOLDER,
    "rotisserie_chicken": ROTISSERIE_CHICKEN_FOLDER,
    "tasty_sides": TASTY_SIDES
}

KITCHEN_CHAT_ID = -1003393413273

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)