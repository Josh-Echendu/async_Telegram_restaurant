# handlers/echo_handler.py - EXACT COPY FROM ORIGINAL FILE
from config import *
from utils.cart_utils import *
from utils.image_utils import *
from .payment_handler import pay_now
from .start_handler import start
from .order_handler import order_meal


async def debug_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # always turn off privacy with /setprivacy so bot can receive all messages sent to group
    print("CHAT ID:", update.effective_chat.id)
    print("CHAT TYPE:", update.effective_chat.type)
    print("CHAT:", update)    

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
        await more_menu_func(update, context)
        
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
        await order_meal(update, context)
        

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

    meal_type = context.user_data.setdefault('meal_type', category)

    # create an empty list to store sent message ids
    context.user_data.setdefault(f"{meal_type}_image_messages", [])

    context.user_data[f'{meal_type}_page'] = 0

    context.user_data.pop(f'{meal_type}_files', None)

    await cart_checkout(update, context)

    # show meal images
    await meal_images(update, context) 
    print("image_ids after meal image: ", context.user_data.get(f'{meal_type}_image_messages', []))  
    print("user_data....: ", context.user_data)