# handlers/start_handler.py - EXACT COPY FROM ORIGINAL FILE
from config import *
from utils.cart_utils import *
from utils.kitchen_utils import *

async def logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
        Logs incoming updates and context for debugging purposes.
    """
    logging.info("Received /start command: %s", context)
    logging.info("Bot details: %s", context.bot)
    logging.info("arguments: %s", context.args)
    logging.info("user_data: %s", context.chat_data)
    logging.info("Update details: %s", update)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await logger(update, context)

    ADMIN_WEB_APP_URL = "https://whoscored.com"

    # ID of the user you want to make admin
    ADMIN_USER_ID = 5680916028

    # chat_id = update.effective_chat.id → get the current chat ID.
    chat_id = update.effective_chat.id

    # user_id = update.effective_user.id → get the ID of the person sending the command.
    user_id = update.effective_user.id

    first_name = update.effective_chat.first_name

    # Detect admin: "If user_id equals ADMIN_USER_ID, then user_is_admin becomes True, otherwise False."
    user_is_admin = user_id == ADMIN_USER_ID

    # ✅ Set WebApp button in input bar (ONLY for admin)
    if user_is_admin:
        await context.bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonWebApp(
                text="🔐 Admin",
                web_app=WebAppInfo(url=ADMIN_WEB_APP_URL)
            )
        )

    # Normal welcome UI
    keyboard = [
        ["🍽 Order Food", "📦 Track Order"],
        ["📞 Contact Staff", "ℹ️ Help"]
    ]

    await update.message.reply_text(
        f"Hello {first_name}! 😊 What would you like to do?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def after_payment(chat_id, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🍽 Order Food", "📦 Track Order"],
        ["📞 Contact Staff", "ℹ️ Help"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text="What would you like to do next?",
        reply_markup=reply_markup
    )