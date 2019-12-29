import telebot
# import pymongo
from menu_config import MENU
# from pymongo import MongoClient


# client = MongoClient()

bot = telebot.TeleBot("939424451:AAFWun0jcSHpXEIOqLH9DP_2OzxRUgsCZ_w")

dishes_list = []
for category in list(MENU.keys()):
    for item in MENU[category]:
        dishes_list.append(item)

cart_list = []
order = {}
msg_make_order = None
orders_in_cart = {}
address = ""
phone_number = ""

back_to_menu_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
back_to_menu_keyboard.add(telebot.types.KeyboardButton(text="В меню"))

make_order_keyboard = telebot.types.InlineKeyboardMarkup()
make_order_keyboard.add(telebot.types.InlineKeyboardButton(
    text="Оформить заказ",
    callback_data='2'))
make_order_keyboard.add(telebot.types.InlineKeyboardButton(
    text="Продолжить покупки",
    callback_data="to_category"
))


# def add_user(user_id, address, phone_number, order):
#     # result = client.users.create_index([('user_id', pymongo.ASCENDING)], unique=True)
#     user = {
#         "user_id": user_id,
#         "address": address,
#         "phone_number": phone_number,
#         "order": order
#     }
#     result = client.users.users.insert_one(user)
    # try:
    # except pymongo.errors.DuplicateKeyError:
    #     print("user is already in database")



def categories(category_list):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for item in category_list:
        keyboard.add(telebot.types.InlineKeyboardButton(text=item, callback_data=item))
    keyboard.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data="to_menu"))
    return keyboard

def cart(cart_list, callback):
    global orders_in_cart
    global msg_make_order
    if not cart_list:
        no_items_in_cart = bot.send_message(
            chat_id=callback.chat.id,
            text="У вас в корзине нет товаров",
            reply_markup=back_to_menu_keyboard
        )
        return no_items_in_cart
    price = 0
    bot.send_message(callback.chat.id, "Корзина" + "\n")
    for category in MENU.keys():
        for item in MENU[category].keys():
            if item in cart_list:
                orders_keyboard = telebot.types.InlineKeyboardMarkup()
                orders_keyboard.add(
                    telebot.types.InlineKeyboardButton(text="(-1)", callback_data=str(item) + "1"),
                    telebot.types.InlineKeyboardButton(text="(+1)", callback_data=str(item) + "2"),
                    telebot.types.InlineKeyboardButton(text="Удалить", callback_data=str(item) + "3")
                )
                price += MENU[category][item]["price"] * cart_list.count(item)
                msg_order = bot.send_message(
                    chat_id=callback.chat.id,
                    text=item + "\n" + MENU[category][item]["desc"] + "\n" + str(MENU[category][item]["price"]) + "P" + " x " + str(cart_list.count(item)),
                    reply_markup=orders_keyboard
                )
                orders_in_cart[item] = {
                    "id": msg_order.message_id,
                    "desc": MENU[category][item]["desc"],
                    "price": MENU[category][item]["price"],
                    "count": cart_list.count(item)
                }
                msg_order

    msg_make_order = bot.send_message(
        chat_id=callback.chat.id,
        text="У вас в корзине заказ на " + str(price) + "P",
        reply_markup=make_order_keyboard
    )
    return msg_make_order

def update_cart(chat_id, callback):
    global msg_make_order
    orders_keyboard = telebot.types.InlineKeyboardMarkup()
    orders_keyboard.add(
        telebot.types.InlineKeyboardButton(text="(-1)", callback_data=str(callback) + "1"),
        telebot.types.InlineKeyboardButton(text="(+1)", callback_data=str(callback) + "2"),
        telebot.types.InlineKeyboardButton(text="Удалить", callback_data=str(callback) + "3")
    )
    orders_in_cart[callback]["count"] = str(cart_list.count(callback))
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=orders_in_cart[callback]["id"],
        text=callback + "\n" + orders_in_cart[callback]["desc"] + "\n" + str(orders_in_cart[callback]["price"]) + "P" + " x " + str(orders_in_cart[callback]["count"]),
        reply_markup=orders_keyboard
        )
    if not cart_list:
        no_items_in_cart = bot.send_message(
            chat_id=chat_id,
            text="У вас в корзине нет товаров",
            reply_markup=back_to_menu_keyboard
        )
        return no_items_in_cart
    price = 0
    for item in orders_in_cart.keys():
        price += int(orders_in_cart[item]["price"]) * int(orders_in_cart[item]["count"])
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg_make_order.message_id,
        text="У вас в корзине заказ на " + str(price) + "P",
        reply_markup=make_order_keyboard
    )





start_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
start_keyboard.row('Меню')
start_keyboard.row('Корзина')
start_keyboard.row('История заказов')
start_keyboard.row('Помощь')





@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Здравствуйте! Вас приветстсвует доставка еды RD Tasty Food!",
        reply_markup=start_keyboard
    )


@bot.message_handler(content_types=['text'])
def reply_keyboard_callbacks(message):
    if message.text == 'Меню' or message.text == "Веринуться к меню" or message.text == "В меню":
        bot.send_message(message.chat.id, "Выберите:", reply_markup=categories(list(MENU.keys())))
    elif message.text == 'Корзина' or message.text == "Отмена":
        cart(cart_list, message)
    elif message.text == 'Доставка':
        order["delivery_option"] = message.text
        msg = bot.send_message(message.chat.id, "Напишите адрес для доставки")
        bot.register_next_step_handler(msg, get_address)
    elif message.text == "Самовывоз":
        order["delivery_option"] = message.text
        phone_number_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        phone_number_keyboard.add(
            telebot.types.KeyboardButton(text="Отправить номер телефона", request_contact=True))
        msg = bot.send_message(message.chat.id, "Отправьте нам номер телефона, чтобы мы могли связаться с Вами",
                         reply_markup=phone_number_keyboard)
        bot.register_next_step_handler(msg, verify)
    elif message.text == "Изменить адрес доставки":
        msg = bot.send_message(message.chat.id, "Напишите новый адрес доставки")
        bot.register_next_step_handler(msg, get_address)
def get_address(message):
    global address
    address = message.text
    phone_number_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    phone_number_keyboard.add(
    telebot.types.KeyboardButton(text="Отправить номер телефона", request_contact=True))
    msg = bot.send_message(message.chat.id, "Отправьте нам номер телефона, чтобы мы могли связаться с Вами", reply_markup=phone_number_keyboard)
    bot.register_next_step_handler(msg, verify)
def verify(message):
    global phone_number
    phone_number = str(message.contact.phone_number)
    # add_user(message.from_user.id, address, phone_number, order)
    # cart_list.clear()
    # orders_in_cart.clear()
    bot.send_message(message.chat.id, "Ваш заказ скоро будет готов. Мы свяжемся с Вами")



@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data in list(MENU.keys()):
        for item in MENU[call.data]:
            price_keyboard = telebot.types.InlineKeyboardMarkup()
            price_keyboard.add(telebot.types.InlineKeyboardButton(
                text=str(MENU[call.data][item]["price"]) + " P",
                callback_data=item)
            )
            price_keyboard.add(telebot.types.InlineKeyboardButton(
                text="Вернуться к выбору категории меню",
                callback_data='to_category'
            ))
            bot.send_message(call.message.chat.id, item + "\n" + MENU[call.data][item]["desc"], reply_markup=price_keyboard)
    elif call.data in dishes_list:
        cart_list.append(call.data)
        cart_keybord = telebot.types.InlineKeyboardMarkup()
        price = 0
        i = cart_list.count(call.data)
        text = ""
        for category in MENU:
            for item in MENU[category].keys():
                if item == call.data:
                    price = MENU[category][item]["price"]
                    text = item + "\n" + MENU[category][item]["desc"]
        cart_keybord.add(telebot.types.InlineKeyboardButton(
            text=str(price) + "P\n" + "Добавлено в корзину" + "("  + str(i) + ")",
            callback_data=call.data
        ))
        cart_keybord.add(
            telebot.types.InlineKeyboardButton(text="Перейти в корзину", callback_data='1')
        )
        cart_keybord.add(telebot.types.InlineKeyboardButton(
            text="Вернуться к выбору категории меню",
            callback_data='to_category'
        ))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=cart_keybord)
    elif call.data[:-1] in dishes_list:
        if call.data[-1] == "1":
            cart_list.remove(call.data[:-1])
            update_cart(call.message.chat.id, call.data[:-1])
        elif call.data[-1] == "2":
            cart_list.append(call.data[:-1])
            update_cart(call.message.chat.id, call.data[:-1])
        elif call.data[-1] == "3":
            cart_list.clear()
            cart(cart_list, call.message)
    elif call.data == '1':
        cart(cart_list, call.message)
    elif call.data == '2':
        order_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        order_keyboard.row("Самовывоз")
        order_keyboard.row("Доставка")
        order_keyboard.row("Отмена")
        bot.send_message(call.message.chat.id,
                         "Укажите вариант доставки", reply_markup=order_keyboard)
    elif call.data == 'to_category':
        bot.send_message(call.message.chat.id, "Выберите:", reply_markup=categories(list(MENU.keys())))
    elif call.data == 'to_menu':
        bot.send_message(call.message.chat.id, "Выберите:",
                         reply_markup=start_keyboard)




def main():
    bot.start_polling()
    
