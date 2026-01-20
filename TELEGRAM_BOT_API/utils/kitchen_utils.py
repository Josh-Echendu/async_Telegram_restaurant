# utils/kitchen_utils.py - EXACT COPY FROM ORIGINAL FILE
from config import *

async def send_to_kitchen(update: Update, context: ContextTypes.DEFAULT_TYPE, query):
    active_cart = context.user_data.get('active_cart', {})
    if not active_cart:
        await query.answer("Cart is empty", show_alert=True)
        return

    copy_cart = active_cart.copy()
    context.user_data.setdefault('order_batches', []).append(copy_cart)

    user = update.effective_user
    price = 1500
    lines = [f"×{qty} - {item} - ₦{price*qty}" for item, qty in copy_cart.items()]
    total = sum(price * qty for qty in copy_cart.values())

    kitchen_text = (
        "🔥 NEW ORDER RECEIVED\n\n"
        f"👤 Customer: {user.first_name}\n"
        f"🆔 User ID: {user.id}\n\n"
        "📦 Items:\n" + "\n".join(lines)+
        f"\n\n——————————\n*Total: ₦{total}*\n\n"
        "⏳ Status: Pending"
    )

    await context.bot.send_message(chat_id=KITCHEN_CHAT_ID, text=kitchen_text)

    context.user_data['active_cart'] = {}
    context.user_data['last_caption'] = {}
    context.user_data.pop("checkout_message_id", None)

    keyboard = [[
        InlineKeyboardButton("➕ Add More Items", callback_data="order_more_items"),
        InlineKeyboardButton("💳 Pay Now", callback_data="pay_now"),
    ]]

    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🍽️ Order sent to the kitchen! 🎉\n\nWhat would you like to do next?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data['send_to_kitchen_id'] = msg.message_id