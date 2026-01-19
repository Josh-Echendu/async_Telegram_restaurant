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


RICE_FOLDER = r"C:\Users\Admin\Music\async_Telegram_restaurant\rice_folder"
SPICED_CHICKEN_FOLDER = r"C:\Users\Admin\Music\async_Telegram_restaurant\spiced_fried_chicken"
FLAMED_GRILLED_CHICKEN = r"C:\Users\Admin\Music\async_Telegram_restaurant\Flamed_grilled_chicken"
BURGER_AND_SNACK_FOLDER = r"C:\Users\Admin\Music\async_Telegram_restaurant\Burger_folder"
BEVERAGES_FOLDER = r"C:\Users\Admin\Music\async_Telegram_restaurant\Beverages"
ROTISSERIE_CHICKEN_FOLDER = r"C:\Users\Admin\Music\async_Telegram_restaurant\Rotisserie_chicken_folder"
TASTY_SIDES = r"C:\Users\Admin\Music\async_Telegram_restaurant\Tasty_sides"

MEAL_FOLDERS = {
    "rice": RICE_FOLDER,
    "spiced_chicken": SPICED_CHICKEN_FOLDER,
    "flamed_grilled_chicken": FLAMED_GRILLED_CHICKEN,
    "burgers_wraps_chickwizz": BURGER_AND_SNACK_FOLDER,
    "beverages": BEVERAGES_FOLDER,
    "rotisserie_chicken": ROTISSERIE_CHICKEN_FOLDER,
    "tasty_sides": TASTY_SIDES
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

    ADMIN_WEB_APP_URL = "https://whoscored.com"

    # ID of the user you want to make admin
    ADMIN_USER_ID = 5680916028

    # chat_id = update.effective_chat.id → get the current chat ID.
    chat_id = update.effective_chat.id

    # user_id = update.effective_user.id → get the ID of the person sending the command.
    user_id = update.effective_user.id

    first_name = update.effective_chat.first_name

    # Detect admin: “If user_id equals ADMIN_USER_ID, then user_is_admin becomes True, otherwise False.”
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
        ['🥤🥗🍔🍗🍟🥓 Snacks', '🍗Flamed Grilled Chicken'],
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

    checkout_msg_id = context.user_data.get('checkout_message_id')
    send_to_kitchen_id = context.user_data.get('send_to_kitchen_id', None)

    # 🔥 If checkout is active and user clicks ANY inline button except allowed ones
    if checkout_msg_id and data not in ("order_to_kitchen", "cancel_order"):
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=query.message.chat.id,
                message_id=checkout_msg_id,
                reply_markup=None
            )
        except:
            pass
        context.user_data.pop("checkout_message_id", None)


    if send_to_kitchen_id and data not in ("add_more_items", "pay_now"):
        try:
            await context.bot.edit_message_text(
                text='🍽️ Order sent to the kitchen! 🎉',
                chat_id=query.message.chat.id,
                message_id=send_to_kitchen_id,
                reply_markup=None
            )
        except:
            pass
        finally:
            context.user_data.pop("send_to_kitchen_id", None)


    # get 'cart' in user_data if not existing setdefault to empty dict
    active_cart = context.user_data.setdefault('active_cart', {})

    # if next page button is clicked
    if data == 'next_page':

        # show meal images for previous page
        meal_type = context.user_data.get('meal_type', None)
        if not meal_type:
            return 

        # appending data to a dict : increment 'rice_page' key by 1
        context.user_data[f"{meal_type}_page"] = context.user_data.get(f'{meal_type}_page', 0) + 1

        # Delete previous buttons
        await query.message.delete()

        await Extract_message_img_ids(update, context)

        await meal_images(update, context)
        print("user_data....: ", context.user_data)


    # if back page button is clicked
    elif data == 'back_page':

        # show meal images for previous page
        meal_type = context.user_data.get('meal_type', None)

        # decrement 'rice_page' key by 1 but not below 0
        context.user_data[f"{meal_type}_page"] = max(context.user_data.get(f'{meal_type}_page', 0) - 1, 0)

        await Extract_message_img_ids(update, context)

        await meal_images(update, context)
        print("user_data....: ", context.user_data)


    # if add button is clicked
    elif data.startswith('add_'):

        # provide alert feedback
        await query.answer("Added 🛒💚", show_alert=False)

        # Extract product name
        product_name = data.replace('add_', '')

        # increment cart by 1
        active_cart[product_name] = active_cart.get(product_name, 0) + 1
        qty = active_cart[product_name]

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
        active_cart[product_name] = max(active_cart.get(product_name, 0) - 1, 0)
        qty = active_cart[product_name]

        await update_qty_button(context, query, product_name, qty)
        print("Remove button clicked: ", context.user_data)

    elif data == 'pay_now':
        if context.user_data.get('send_to_kitchen_id'):
            context.user_data.pop('send_to_kitchen_id', None)
        await pay_now(update, context, query)

    elif data == 'cancel_order':
        await query.answer("❌ Order cancelled")
        context.user_data.pop("checkout_message_id", None)

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

        photo_url = r'C:\Users\Admin\Music\async_Telegram_restaurant\photo_2026-01-09 14.59.50.jpeg'

        input_file = InputFile(open(photo_url, 'rb'))

        await context.bot.send_photo(
            chat_id=query.message.chat.id,
            caption="🎉 Your payment has been received! Thank you for choosing our service! 🍽️😊",
            photo=input_file
        )

        # Clear cart and unlock cart
        context.user_data['active_cart'] = {}
        context.user_data['order_batches'] = []
        context.user_data['last_caption'] = {}
        context.user_data['cart_locked'] = False

        print("user_data_after_payment: ", context.user_data)

        await after_payment(query.message.chat.id, context)
    
    elif data == "order_to_kitchen":
        await query.edit_message_reply_markup(reply_markup=None)
        await send_to_kitchen(update, context, query)

    elif data == "add_more_items":
        if context.user_data.get('send_to_kitchen_id'):
            context.user_data.pop('send_to_kitchen_id', None)
        await query.edit_message_text("🍽️ Order sent to the kitchen! 🎉")

        # Extract message chat.id bcos update.message for a callback_query is None
        await order_meal_by_chat_id(query.message.chat.id, context)

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
    active_cart = context.user_data.get('active_cart', {})

    # send images for current page
    for path in page_items:

        # Extract product name from file name
        product_name = os.path.basename(path).replace(".jpg","")

        # get current quantity in cart, if not exist default to 
        active_cart_count = active_cart.get(product_name, 0)

        # create inline keyboard for the product
        product_keyboard = [
            [
                InlineKeyboardButton("🛒💚", callback_data=f"add_{product_name}"),
                InlineKeyboardButton(f"⚖️ {active_cart_count}", callback_data="noop"),
                InlineKeyboardButton("🛍️➖", callback_data=f"remove_{product_name}"),
            ]
        ]

        # check if there is a last caption for the product i.e  if a add/remove button was clicked before
        if 'last_caption' in context.user_data and product_name in context.user_data['last_caption']:
            try:
                caption = context.user_data['last_caption'][product_name]
                with open(path, 'rb') as f:
                    send_msg = await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=InputFile(f),
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(product_keyboard)
                    )
                
                # store sent message id into meal_image_messages list
                context.user_data.setdefault(f'{meal_type}_image_messages', []).append(send_msg.message_id)
            except Exception as e:
                logging.warning(f"Failed to send image {path}: {e}")

        else:
            try:
                with open(path, 'rb') as f:
                    send_msg = await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=InputFile(f),
                        caption=f"{product_name} - ₦{price}",
                        reply_markup=InlineKeyboardMarkup(product_keyboard)
                    )

                # store sent message id into meal_image_messages list
                context.user_data.setdefault(f'{meal_type}_image_messages', []).append(send_msg.message_id)
            except Exception as e:
                logging.warning(f"Failed to send image {path}: {e}")


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

    checkout_msg_id = context.user_data.get('checkout_message_id', None)
    send_to_kitchen_id = context.user_data.get('send_to_kitchen_id', None)
    
    if checkout_msg_id:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=update.effective_chat.id,
                message_id=checkout_msg_id,
                reply_markup=None
            )
        except:
            pass
        finally:
            context.user_data.pop("checkout_message_id", None)

    if send_to_kitchen_id:
        try:
            await context.bot.edit_message_text(
                text='🍽️ Order sent to the kitchen! 🎉',
                chat_id=update.effective_chat.id,
                message_id=send_to_kitchen_id,
                reply_markup=None
            )
        except:
            pass
        finally:
            context.user_data.pop("send_to_kitchen_id", None)


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
        more_menu = context.user_data.get("more_menu")
        
        # if there is a meal_type in user_data, go back to meal ordering menu
        if meal_type:
            await Extract_message_img_ids(update, context)
            await order_meal(update, context)
            return
        
        if more_menu:
            context.user_data.pop('more_menu', None)
            await order_meal(update, context)
            return

        await start(update, context)

    elif text == "🍚 🍚 🍚Rice":
        await echo_orders(update, context, category='rice')

    elif text == "🍗🍗Spiced Fried Chicken":
        await echo_orders(update, context, category='spiced_chicken')  

    elif text == "🍗Flamed Grilled Chicken":
        await echo_orders(update, context, category='flamed_grilled_chicken')  

    elif text == "🥗🍔🍗🍟🥓 Snacks":
        await echo_orders(update, context, category='burgers_wraps_chickwizz')  

    elif text == "🥤🍾🍷 Drinks / Beverages":
        await echo_orders(update, context, category='beverages')  
    
    elif text == "🍗🍗 Rotisserie Chicken":
        await echo_orders(update, context, category='rotisserie_chicken')  
        
    elif text == "🍗🍝 🍜Tasty Sides":
        await echo_orders(update, context, category='tasty_sides')  
        
    elif text == "➡️ More":
        context.user_data.setdefault("more_menu", True)
        await cart_checkout(update, context)
        
    elif text == "🛍️✅💳 Checkout/Pay":
        # 1️⃣ Try paying for current cart if not empty
        if context.user_data.get('active_cart'):
            await checkout_pay(update, context)
            return
        
        # 2️⃣ If cart empty, but last_order exists (sent to kitchen), allow paying it
        last_order = context.user_data.get('order_batches', [])
        if last_order:
            await pay_now(update, context)
            return
        
        # 3️⃣ Otherwise, truly empty cart and no order_batches
        await Extract_message_img_ids(update, context)
        await update.message.reply_text(
            "🛒 Your cart is empty.\nPlease add items before paying."
        )
        

    elif text == "🛒💚 View Cart":
        meal_type = context.user_data.get('meal_type')
        
        if not meal_type:
            return 
        
        active_cart = context.user_data.get('active_cart')
        
        if not active_cart:
           
            await Extract_message_img_ids(update, context)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You have no cart items!"
            )
            

            # Go back to meal category
            await order_meal(update, context)
            return


async def echo_orders(update: Update, context: ContextTypes.DEFAULT_TYPE, category):
    if context.user_data.get('meal_type'):
        context.user_data.pop('meal_type', None)

    meal_type = context.user_data.get('meal_type', None)

    # create an empty list to store sent message ids
    context.user_data.setdefault(f"{meal_type}_image_messages", [])

    context.user_data[f'{meal_type}_page'] = 0

    context.user_data.pop(f'{meal_type}_files', None)

    await cart_checkout(update, context)

    # show meal images
    await meal_images(update, context) 
    print("image_ids after meal image: ", context.user_data.get(f'{meal_type}_image_messages', []))  
    print("user_data....: ", context.user_data)

async def Extract_message_img_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meal_type = context.user_data.get('meal_type')
    if not meal_type:
        return

    old_ids = context.user_data.get(f"{meal_type}_image_messages", []).copy()
    context.user_data[f"{meal_type}_image_messages"] = []

    if old_ids:
        await asyncio.gather(
            *[delete_image(update, context, msg_id) for msg_id in old_ids],
            return_exceptions=True
        )


async def delete_image(update: Update, context: ContextTypes.DEFAULT_TYPE, message_id):
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=message_id
        )
    except Exception as e:
        logging.error(f"Error deleting message {message_id}: {e}")
        pass  # message may already be deleted

KITCHEN_CHAT_ID = -1003393413273
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
        InlineKeyboardButton("➕ Add More Items", callback_data="add_more_items"),
        InlineKeyboardButton("💳 Pay Now", callback_data="pay_now"),
    ]]

    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🍽️ Order sent to the kitchen! 🎉\n\nWhat would you like to do next?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data['send_to_kitchen_id'] = msg.message_id


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

async def global_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 🔒 Only lock PRIVATE chats, never groups
    if update.effective_chat.type != "private":
        return
    
    if not context.user_data.get('cart_locked'):
        return

    # Block normal messages + reply buttons
    if update.message:
        try:
            await update.message.delete()
        except:
            pass
        await update.message.chat.send_message(
            "💳 Payment in progress.\nPlease complete or cancel payment to continue."
        )

    # Block inline buttons
    elif update.callback_query:
        await update.callback_query.answer(
            "💳 Payment in progress.\nPlease complete or cancel payment to continue.",
            show_alert=True
        )

    raise ApplicationHandlerStop

async def debug_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # always turn off privacy with /setprivacy so bot can receive all messages sent to group
    print("CHAT ID:", update.effective_chat.id)
    print("CHAT TYPE:", update.effective_chat.type)
    print("CHAT:", update)


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
