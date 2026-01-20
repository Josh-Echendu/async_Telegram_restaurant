# handlers/button_handler.py - EXACT COPY FROM ORIGINAL FILE
from config import *
import telegram
from utils.cart_utils import *
from utils.image_utils import *
from utils.kitchen_utils import *
from .payment_handler import pay_now
from .start_handler import after_payment
from .order_handler import order_meal_by_chat_id

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


    if send_to_kitchen_id and data not in ("order_more_items", "pay_now"):
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

    elif data == "order_more_items":
        if context.user_data.get('send_to_kitchen_id'):
            context.user_data.pop('send_to_kitchen_id', None)
        await query.edit_message_text("🍽️ Order sent to the kitchen! 🎉")

        # Extract message chat.id bcos update.message for a callback_query is None
        await order_meal_by_chat_id(query.message.chat.id, context)