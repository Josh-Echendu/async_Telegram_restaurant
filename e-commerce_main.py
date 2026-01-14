from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ChatPermissions  # Update → Represents an incoming update from Telegram, like a message or command.
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext # ContextTypes → Provides the context for the message or chat, like info about who sent it, what chat it came from, etc.
from telegram.ext import MessageHandler, filters, CallbackQueryHandler
from telegram.ext import ChatMemberHandler
import logging
from telegram import ReplyKeyboardRemove
from telegram import ChatMember
import asyncio
import zipfile
from telegram import InputFile
import shutil
import glob
from telegram import Update
from telegram.ext import ContextTypes
import os
from telegram import InputFile, Update, InlineKeyboardButton, InlineKeyboardMarkup


RICE_FOLDER = r"/Users/joshua.echendu/Documents/async_Telegram_restaurant/rice_folder"
SPICED_CHICKEN_FOLDER = r"/Users/joshua.echendu/Documents/async_Telegram_restaurant/spiced_fried_chicken"
ROTISSERIE_CHICKEN_FOLDER = r"/Users/joshua.echendu/Documents/async_Telegram_restaurant/Rotisserie_chicken"
BURGER_AND_SNACK_FOLDER = r"/Users/joshua.echendu/Documents/async_Telegram_restaurant/Burger_folder"
BEVERAGES_FOLDER = r"/Users/joshua.echendu/Documents/async_Telegram_restaurant/Beverages"

MEAL_FOLDERS = {
    "rice": RICE_FOLDER,
    "spiced_chicken": SPICED_CHICKEN_FOLDER,
    "rotisserie_chicken": ROTISSERIE_CHICKEN_FOLDER,
    "burgers_wraps_chickwizz": BURGER_AND_SNACK_FOLDER,
    "beverages": BEVERAGES_FOLDER
}


async def logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
        Logs incoming updates and context for debugging purposes.
    """
    logging.info("Received /start command: %s", context)
    logging.info("Bot details: %s", context.bot)
    logging.info("arguments: %s", context.args)
    logging.info("user_data: %s", context.chat_data)
    logging.info("Update details: %s", update)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await logger(update, context)
    first_name = update.effective_chat.first_name

    keyboard = [
        ["🍽 Order Food", "📦 Track Order"],
        ["📞 Contact Staff", "ℹ️ Help"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await update.message.reply_text(
        text=f"Hello, {first_name}! 😊 Welcome to our service. How can we assist you today? 😊",
        reply_markup=reply_markup
    )

    print("context", context.bot)
    print("update", update)

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

async def order_meal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reply_keyboard = [
        ["🍚 🍚 🍚Rice", "🍗🍗Spiced Fried Chicken"],
        ['🥗🍔🍗🍟🥓 Snacks', '🍗Rotisserie Chicken'],
        ["⬅️ Back", "🥤🍾🍷 Drinks / Beverages"],
        

        # ["🛍️✅💳 Checkout/Pay"]
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
        ['🥤🥗🍔🍗🍟🥓 Snacks', '🍗Rotisserie Chicken'],
        ["⬅️ Back", "🥤 Drinks / Beverages"],
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

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # get 'cart' in user_data if not existing setdefault to empty dict
    cart = context.user_data.setdefault('cart', {})

    # 🚫 If cart is locked, prevent modifications
    if context.user_data.get('cart_locked'):

        # if user tries to modify cart during checkout
        if data.startswith(("add_", "remove_", "next_page", "back_page")):
            await query.answer(
                "Checkout in progress. Please pay or cancel your order.",
                show_alert=True
            )
            return

    # if next page button is clicked
    if data == 'next_page':

        # show meal images for previous page
        meal_type = context.user_data.get('meal_type', None)
        if not meal_type:
            return 

        # appending data to a dict : increment 'rice_page' key by 1
        context.user_data[f"{meal_type}_page"] = context.user_data.get(f'{meal_type}_page', 0) + 1
        
        # Extract the 3 previous page message ids
        meal_image_messages_ids = context.user_data.get(f"{meal_type}_image_messages", [])
        print("meal_images_id: ", meal_image_messages_ids)

        # Delete previous buttons
        await query.message.delete()

        # Extract old image ids
        old_ids = context.user_data.get(f'{meal_type}_image_messages', []).copy()

        # Clear the meal_image_messages list before deletion
        context.user_data[f'{meal_type}_image_messages'] = []

        if old_ids:  
            # delete previous image messages
            await Extract_message_img_ids(update, context, old_ids)

        await meal_images(update, context)


    # if back page button is clicked
    elif data == 'back_page':

        # show meal images for previous page
        meal_type = context.user_data.get('meal_type', None)

        # decrement 'rice_page' key by 1 but not below 0
        context.user_data[f"{meal_type}_page"] = max(context.user_data.get(f'{meal_type}_page', 0) - 1, 0)

        # Extract the 3 previous page message ids
        meal_image_messages_ids = context.user_data.get(f"{meal_type}_image_messages", [])
        print("meal_images_id: ", meal_image_messages_ids)

        # Extract old image ids
        old_ids = context.user_data.get(f'{meal_type}_image_messages', []).copy()

        # Clear the meal_image_messages list before deletion
        context.user_data[f'{meal_type}_image_messages'] = []

        if old_ids:  
            # delete previous image messages
            await Extract_message_img_ids(update, context, old_ids)

        await meal_images(update, context)

    # if add button is clicked
    elif data.startswith('add_'):

        # provide alert feedback
        await query.answer("Added 🛒💚", show_alert=False)

        # Extract product name
        product_name = data.replace('add_', '')

        # increment cart value by 1
        cart[product_name] = cart.get(product_name, 0) + 1
        qty = cart[product_name]

        await update_qty_button(context, query, product_name, qty)
        print("ADD button clicked: ", context.user_data)

    # if remove button is clicked
    elif data.startswith('remove_'):
        # print("Remove button clicked: ", context.user_data)

        # provide alert feedback
        await query.answer("Removed 🛍️➖", show_alert=False)

        # Extract product name
        product_name = data.replace('remove_', '')

        # Decrement cart value by 1 but not below 0
        cart[product_name] = max(cart.get(product_name, 0) - 1, 0)
        qty = cart[product_name]

        await update_qty_button(context, query, product_name, qty)
        print("Remove button clicked: ", context.user_data)

    elif data == 'pay_now':
        # Charge user based on backend cart
        cart = context.user_data.get('cart', {})
        total_amount = sum(qty * 1500 for qty in cart.values()) # Assuming each item costs 1500

        # delete the Transfer and cancel buttons
        await query.edit_message_reply_markup(reply_markup=None)


        keyboard = [
            [
                InlineKeyboardButton("✅ I have paid", callback_data="confirm_payment"),
                InlineKeyboardButton(f"[ ❌ Cancel ]", callback_data="cancel_order"),
            ]
        ]

        account_info = "Bank: XYZ Bank\nAccount Number: 1234567890\nAccount Name: ABC Restaurant"
        await query.message.reply_text(
            f"Please make your payment to the following account:\n\n{account_info}\n\nThank you for your order!",   
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    elif data == 'cancel_order':
        await query.answer("❌ Order cancelled")

        # Unlock cart
        context.user_data['cart_locked'] = False
        print("query message: ", query)
        await query.message.reply_text("Your order has been cancelled. You can continue ordering.")
        try:
            await query.message.delete()

        except Exception as e:
            logging.error(f"Error deleting message: {e}")
            pass  # message may already be deleted

        finally:

            # Extract message chat.id bcos update.message for a callback_query is None
            await order_meal_by_chat_id(query.message.chat.id, context)

    elif data == 'confirm_payment':
        await query.answer("✅ Payment confirmed. Thank you!")

        await query.edit_message_reply_markup(reply_markup=None)

        photo_url = '/Users/joshua.echendu/Documents/async_Telegram_restaurant/photo_2026-01-09 14.59.50.jpeg'

        input_file = InputFile(open(photo_url, 'rb'))

        await context.bot.send_photo(
            chat_id=query.message.chat.id,
            caption="🎉 Your payment has been received! Your order is being prepared and will be delivered shortly. Thank you for choosing our service! 🍽️😊",
            photo=input_file
        )
        # Clear cart and unlock cart
        context.user_data['cart'] = {}
        context.user_data['last_caption'] = {}
        context.user_data['cart_locked'] = False

        await after_payment(query.message.chat.id, context)


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

async def meal_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = 1500
    ITEMS_PER_PAGE = 3

    meal_type = context.user_data.get('meal_type', None)

    #  if 'rice_files' not in user_data, load all rice image files
    if f'{meal_type}_files' not in context.user_data:

        # store all rice image files in user_data i.e cache rice image files
        context.user_data[f'{meal_type}_files'] = glob.glob(os.path.join(MEAL_FOLDERS[meal_type], '*.jpg'))

    # if no rice_page key initialize it with 0
    page = context.user_data.get(f'{meal_type}_page', 0)

    # calculate start indices for current page
    start_idx = page * ITEMS_PER_PAGE

    # calculate end indices for current page
    end_idx = start_idx + ITEMS_PER_PAGE

    # get the rice file list from user_data
    file_list = context.user_data[f'{meal_type}_files']

    # slice the file list for current page
    page_items = file_list[start_idx:end_idx]

    # get current cart, if not exist create empty dict
    cart = context.user_data.get('cart', {})

    # send images for current page
    for path in page_items:

        # Extract product name from file name
        product_name = os.path.basename(path).replace(".jpg","")

        # get current quantity in cart, if not exist default to 
        cart_count = cart.get(product_name, 0)

        # create inline keyboard for the product
        product_keyboard = [
            [
                InlineKeyboardButton("🛒💚", callback_data=f"add_{product_name}"),
                InlineKeyboardButton(f"⚖️ {cart_count}", callback_data="noop"),
                InlineKeyboardButton("🛍️➖", callback_data=f"remove_{product_name}"),
            ]
        ]

        # check if there is a last caption for the product i.e  if a add/remove button was clicked before
        if 'last_caption' in context.user_data and product_name in context.user_data['last_caption']:
            caption = context.user_data['last_caption'][product_name]
            with open(path, 'rb') as f:
                send_msg = await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=InputFile(f),
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(product_keyboard)
                )
            
            # store sent message id into meal_image_messages list
            context.user_data.get(f'{meal_type}_image_messages', []).append(send_msg.message_id)

        else:
            with open(path, 'rb') as f:
                send_msg = await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=InputFile(f),
                    caption=f"{product_name} - ₦{price}",
                    reply_markup=InlineKeyboardMarkup(product_keyboard)
                )

            # store sent message id into meal_image_messages list
            context.user_data.get(f'{meal_type}_image_messages', []).append(send_msg.message_id)


    # navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data="back_page"))
    if end_idx < len(file_list):
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data="next_page"))

    if nav_buttons:
        back_next_msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Use buttons to navigate:",
            reply_markup=InlineKeyboardMarkup([nav_buttons])
        )
        # store sent message id into meal_image_messages list
        context.user_data.get(f'{meal_type}_image_messages', ).append(back_next_msg.message_id)   

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    if text == "🍽 Order Food":
        await order_meal(update, context)

    elif text == "📦 Track Order":
        await update.message.reply_text("Coming soon 😊.")
    
    elif text == "📞 Contact Staff":
        first_name = update.effective_chat.first_name
        await update.message.reply_text(f"Good day {first_name} 😊, to contact us you call us on \n\n CONTACT: +234 906 393 8743.")

    elif text == "ℹ️ Help":
        await update.message.reply_text("You have chosen to get help.")
    
    elif text == "⬅️ Back":
        meal_type = context.user_data.get('meal_type')

        # if there is a meal_type in user_data, go back to meal ordering menu
        if meal_type:
            await order_meal(update, context)

            # Extract the previous page message ids
            meal_image_messages_ids = context.user_data.get(f"{meal_type}_image_messages", [])
            print("meal_images_id: ", meal_image_messages_ids)

            # Extract old image ids
            old_ids = context.user_data.get(f'{meal_type}_image_messages', []).copy()

            # Clear the meal_image_messages list before deletion
            context.user_data[f'{meal_type}_image_messages'] = []

            # remove meal_type from user_data
            context.user_data.pop('meal_type', None)

            if old_ids:  
                # delete previous image messages
                await Extract_message_img_ids(update, context, old_ids)

            return
        await start(update, context)

    elif text == "🍚 🍚 🍚Rice":
        await echo_orders(update, context, category='rice')

    elif text == "🍗🍗Spiced Fried Chicken":
        await echo_orders(update, context, category='spiced_chicken')  

    elif text == "🍗Rotisserie Chicken":
        await echo_orders(update, context, category='rotisserie_chicken')  

    elif text == "🥗🍔🍗🍟🥓 Snacks":
        await echo_orders(update, context, category='burgers_wraps_chickwizz')  

    elif text == "🥤🍾🍷 Drinks / Beverages":
        await echo_orders(update, context, category='beverages')  
        
    elif text == "🛍️✅💳 Checkout/Pay":
        await checkout_pay(update, context)


async def echo_orders(update: Update, context: ContextTypes.DEFAULT_TYPE, category):
    if context.user_data.get('meal_type'):
        context.user_data.pop('meal_type', None)

    meal_type = context.user_data['meal_type'] = category

    # create an empty list to store sent message ids
    context.user_data.setdefault(f"{meal_type}_image_messages", [])
    print("user_data....: ", context.user_data)

    context.user_data[f'{meal_type}_page'] = 0

    context.user_data.pop(f'{meal_type}_files', None)

    await cart_checkout(update, context)

    # show meal images
    await meal_images(update, context) 
    print("image_ids after meal image: ", context.user_data.get(f'{meal_type}_image_messages', []))    

async def Extract_message_img_ids(update: Update, context: ContextTypes.DEFAULT_TYPE, list_of_message_ids: list):

    # Delete all previous meal messages ids concurrently
    task = [delete_image(update, context, msg_id) for msg_id in list_of_message_ids]
    await asyncio.gather(*task, return_exceptions=True)

async def delete_image(update: Update, context: ContextTypes.DEFAULT_TYPE, message_id):
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=message_id
        )
    except Exception as e:
        logging.error(f"Error deleting message {message_id}: {e}")
        pass  # message may already be deleted

async def checkout_pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meal_type = context.user_data.get('meal_type', None)
    if not meal_type:
        return

    # get the current cart
    cart = context.user_data.get('cart', {})

    if not cart:
        # if no cart items display this message
        no_cart_msg_id = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🛒💚 Your cart is empty. Please add items before checking out 😊😊."
        )
        context.user_data.get(f'{meal_type}_image_messages', []).append(no_cart_msg_id)
        print(context.user_data.get(f'{meal_type}_image_messages', []))
        
        # Go back to meal category
        await order_meal(update, context)

        # Extract old image ids
        old_ids = context.user_data.get(f'{meal_type}_image_messages', []).copy()

        # Clear the meal_image_messages list before deletion
        context.user_data[f'{meal_type}_image_messages'] = []

        if old_ids:  
            # delete previous image messages
            await Extract_message_img_ids(update, context, old_ids)
        
        return

    # Lock the cart to prevent further modifications
    context.user_data['cart_locked'] = True

    # Extract all previous meal messages ids
    meal_image_messages_ids = context.user_data.get(f'{meal_type}_image_messages', [])

    old_ids = context.user_data.get(f'{meal_type}_image_messages', []).copy()

    context.user_data[f"{meal_type}_image_messages"] = []

    # Delete all previous meal messages ids concurrently
    task = [delete_image(update, context, msg_id) for msg_id in old_ids]
    await asyncio.gather(*task, return_exceptions=True)

    # Build checkout summary dynamically
    price = 1500
    lines = []

    # Calculate total price
    total_price = sum(price * qty for item, qty in cart.items())

    for item, qty in cart.items():
        subtotal = price * qty
        lines.append(f"X{qty}- {item} - ₦{subtotal}")

    summary = (
        "🧾 *Your Order Summary*\n\n"
        + "\n".join(lines)
        + f"\n\n——————————\n*Total: ₦{total_price}*"
    )

    keyboard = [
        [
            InlineKeyboardButton("🏦 Bank Transfer ", callback_data=f"pay_now"),
            InlineKeyboardButton(f"[ ❌ Cancel ]", callback_data="cancel_order"),
        ]
    ]
    await update.message.reply_text(
        text=summary,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def cart_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🛍️✅💳 Checkout/Pay"],
        ["⬅️ Back"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await update.message.reply_text("Here are the options for Today 🍟🍟🍟:", reply_markup=reply_markup)



if __name__ == '__main__':
    logging.info("Starting bot...")

    app = ApplicationBuilder().token("8579347588:AAF7dD-b2QlHWEeaounsrixZtle_wB_8VfY").build()
    start_handler = CommandHandler(command='start', callback=start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    app.add_handler(echo_handler)
    app.add_handler(start_handler)
    app.add_handler(CallbackQueryHandler(button_click))

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
