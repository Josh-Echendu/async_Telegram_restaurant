# handlers/order_handler.py - EXACT COPY FROM ORIGINAL FILE
from config import *
from utils.cart_utils import *
from utils.image_utils import *

async def order_meal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reply_keyboard = [
        ["🍚 🍚 🍚Rice", "🍗🍗Spiced Fried Chicken"],
        ['🥗🍔🍗🍟🥓 Snacks', '🍗Flamed Grilled Chicken'],
        ['🍗🍗 Rotisserie Chicken', '🍗🍝 🍜Tasty Sides'],
        ["⬅️ Back", "➡️ More"]
    ]

    markup = ReplyKeyboardMarkup(
        reply_keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await update.message.reply_text("Please Select a category in the menu below 👇:", reply_markup=markup)

async def order_meal_by_chat_id(chat_id, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ["🍚 🍚 🍚Rice", "🍗🍗Spiced Fried Chicken"],
        ['🥗🍔🍗🍟🥓 Snacks', '🍗Flamed Grilled Chicken'],
        ['🍗🍗 Rotisserie Chicken', '🍗🍝 🍜Tasty Sides'],
        ["⬅️ Back", "➡️ More"]
    ]

    markup = ReplyKeyboardMarkup(
        reply_keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text="Please Select a category in the menu below 👇:",
        reply_markup=markup
    )