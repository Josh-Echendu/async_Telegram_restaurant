# utils/image_utils.py - EXACT COPY FROM ORIGINAL FILE
from config import *


async def meal_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = 1500
    ITEMS_PER_PAGE = 3

    meal_type = context.user_data.get('meal_type', None)
    print("user_data: ", context.user_data)

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