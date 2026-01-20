# utils/cart_utils.py - EXACT COPY FROM ORIGINAL FILE
from config import *
import telegram
from utils.image_utils import Extract_message_img_ids

async def update_qty_button(context, query, product_name, qty, price_per_item=1500):
    
    # Extract the inline keyboard list from the message
    keyboard = query.message.reply_markup.inline_keyboard
    print("keyboard type:", keyboard)
    print('First row of keyboard:', keyboard[0][1])
    print("query:", query)
    print("query message caption:", query.message.caption)
    print("Existing keyboard:", keyboard)

    new_keyboard = []
    changed = False

    for row in keyboard:
        new_row = []
        for button in row:
            if button.callback_data == f"add_{product_name}":
                new_row.append(button)

            elif button.callback_data == f"remove_{product_name}":
                new_row.append(button)

            elif button.callback_data == "noop":

                # extract old qty from text
                old_qty = int(button.text.replace("⚖️ ", "").strip())
                if old_qty != qty:
                    changed = True

                # replace qty button
                new_row.append(
                    InlineKeyboardButton(f"⚖️ {qty}", callback_data="noop")
                )
            else:
                new_row.append(button)
                
        new_keyboard.append(new_row)

    # Calculate total price
    total_price = qty * price_per_item  # Assuming each item costs 1500
    new_caption = f"{product_name} - ₦{price_per_item} \nQty: {qty} | Total: ₦{total_price}"

    # 🚫 If nothing changed, DO NOTHING (avoid Telegram error)
    if not changed and query.message.caption == new_caption:
        return

    # Edit message caption and keyboard in one go
    try:
        caption = await query.edit_message_caption(
        caption=new_caption,
        reply_markup=InlineKeyboardMarkup(new_keyboard)
    )
    except telegram.error.BadRequest:
        pass

    finally:
        if caption:
            print("Caption updated successfully.")
            context.user_data.setdefault('last_caption', {})[product_name] = new_caption


async def cart_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🛒💚 View Cart", "🛍️✅💳 Checkout/Pay"],
        ["⬅️ Back"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await update.message.reply_text("Select an item from the menu below:", reply_markup=reply_markup)

    # await update.message.reply_text("Here are the options for Today 🍟🍟🍟:", reply_markup=reply_markup)

async def more_menu_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['🥤🍾🍷 Drinks / Beverages'],
        ["🛒💚 View Cart", "🛍️✅💳 Checkout/Pay"],
        ["⬅️ Back"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await update.message.reply_text("Select an item from the menu below:", reply_markup=reply_markup)

    # await update.message.reply_text("Here are the options for Today 🍟🍟🍟:", reply_markup=reply_markup)


async def checkout_pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meal_type = context.user_data.get('meal_type', None)
    if not meal_type:
        return

    # get the current cart
    active_cart = context.user_data.get('active_cart', {})
    print("active_cart...: ", active_cart)
    
    if not active_cart:

        await Extract_message_img_ids(update, context)
        await update.message.reply_text(
            "🛒 Your cart is empty.\nPlease add items before paying."
        )
        return

    # Delete all previous meal messages ids concurrently
    await Extract_message_img_ids(update, context)

    # Build checkout summary dynamically
    price = 1500
    lines = []

    # Calculate total price
    total_price = sum(price * qty for item, qty in active_cart.items())

    for item, qty in active_cart.items():
        subtotal = price * qty
        lines.append(f"X{qty}- {item} - ₦{subtotal}")

    summary = (
        "🧾 *Your Order Summary*\n\n"
        + "\n".join(lines)
        + f"\n\n——————————\n*Total: ₦{total_price}*"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Send to Kitchen", callback_data=f"order_to_kitchen"),
            InlineKeyboardButton(f"[ ❌ Cancel ]", callback_data="cancel_order"),
        ]
    ]
    msg = await update.message.reply_text(
        text=summary,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Extract checkout_message_id
    context.user_data['checkout_message_id'] = msg.message_id
    print("checkout_id: ", context.user_data['checkout_message_id'])