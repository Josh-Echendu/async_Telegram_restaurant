# main.py - EXACT COPY FROM ORIGINAL FILE (with imports adjusted)
from config import *
from handlers.start_handler import start
from handlers.button_handler import button_click
from handlers.echo_handler import echo, debug_chat
from handlers.order_handler import order_meal

async def global_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    # get cart lock status
    cart_locked = context.user_data.get('cart_locked', False)

    # # allow some exceptions even if cart is locked
    allowed_callbacks = ["confirm_payment", "cancel_order"]

    if update.callback_query and update.callback_query.data in allowed_callbacks:
        return  # let these go through

    # if cart is not locked
    if not cart_locked:
        return

    # Block normal messages
    if update.message:
        try:
            await update.message.delete()
        except:
            pass
        await update.message.chat.send_message(
            "💳 Payment in progress.\nPlease complete or cancel payment to continue."
        )

    # Block other inline buttons
    elif update.callback_query:
        await update.callback_query.answer(
            "💳 Payment in progress.\nPlease complete or cancel payment to continue.",
            show_alert=True
        )

    raise ApplicationHandlerStop


if __name__ == '__main__':
    logging.info("Starting bot...")

    app = ApplicationBuilder().token("8579347588:AAF7dD-b2QlHWEeaounsrixZtle_wB_8VfY").build()
    # app = ApplicationBuilder().token("8571806750:AAFOY6-QdejiSOthWBkJK3ufR4I2FYpV31Q").build()

    # 🔒 Guards — catch EVERYTHING first
    app.add_handler(MessageHandler(filters.ALL, global_guard), group=0)
    app.add_handler(CallbackQueryHandler(global_guard), group=0)

    # 🚦 Actual logic — only runs if guard allows
    app.add_handler(CommandHandler("start", start), group=1)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo), group=1)
    app.add_handler(CallbackQueryHandler(button_click), group=1)
    app.add_handler(MessageHandler(filters.ALL, debug_chat), group=99)


    app.run_polling()


# for my telegeram bot , when a user carts to cart, we have a back 2 reply button in which user can go back to and add more food category and pay/checkout, when a user clicks checkout we immediately lock all inline buttons to avoid users from maliciously malipulating prices , so imagine a user order 3 items , any in the checkout and back button 


# ⚡ Recommended flow for your bot

# User clicks Checkout / Pay

# Set context.user_data['cart_locked'] = True.

# Delete all previous meal messages (loop through stored message_ids).

# Build fresh summary message from backend cart.

# Send it with buttons: Pay / Cancel.

# If user clicks Cancel

# Unlock cart: context.user_data['cart_locked'] = False.

# Optionally let them browse again.

# If user clicks Pay

# Charge total based on backend cart.

# Reset cart and cart_locked.