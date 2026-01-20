# handlers/payment_handler.py - EXACT COPY FROM ORIGINAL FILE
from config import *
from utils.kitchen_utils import send_to_kitchen
from handlers.start_handler import after_payment

async def pay_now(update, context, query=None):
    context.user_data['cart_locked'] = True
    price = 1500

    # Charge user based on backend cart
    order_batches = context.user_data.get('order_batches', [])

    lines = []
    total_price = 0

    if query:
        # delete the Transfer and cancel buttons
        await query.edit_message_text("🍽️ Order sent to the kitchen! 🎉")

    for order in order_batches:
        for item, qty in order.items():
            subtotal = price * qty
            total_price = total_price + subtotal
            lines.append(f"{qty}X - {item} - ₦{subtotal}")

    account_info = "Bank: XYZ Bank\nAccount Number: 1234567890\nAccount Name: ABC Restaurant"
    summary = (
        "🧾 *Your Order Summary*\n\n"
        + "\n".join(lines)
        + f"\n\n——————————\n*Total: ₦{total_price}*"
        + f"\n\nPlease make your payment to the following account:\n\n{account_info}\n\nThank you for your order!"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ I have paid", callback_data="confirm_payment"),
        ]
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=summary,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )