import telebot
from telebot import types
import sqlite3
import datetime
import random
import string
import logging
import os
from fpdf import FPDF
from datetime import datetime

API_TOKEN = '8194580197:AAH7UJ14gzSFKJxMc4s5tyJHXlix2QNDj2Q'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 558372164
FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts')
FONT_PATH = os.path.join(FONT_DIR, 'DejaVuSans.ttf')

logging.basicConfig(
    filename='bot_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if not os.path.exists(FONT_DIR):
    os.makedirs(FONT_DIR)

user_cart = {}
adding_product = {}
order_data = {}
temp_data = {}

messages = {
    'ua': {
        'welcome': "Привіт! Оберіть дію з меню нижче:",
        'info': "Цей бот допомагає вам замовляти товари з нашого каталогу.",
        'catalog': "Ось доступні товари:",
        'back': "🔙 Назад",
        'add_to_cart': "🛒 Додати до корзини",
        'cart_empty': "Ваша корзина порожня.",
        'order_name': "Введіть ваше ім'я:",
        'order_lastname': "Введіть прізвище:",
        'order_phone': "Надішліть ваш номер телефону:",
        'order_city': "Введіть місто доставки:",
        'thanks': "Дякуємо за замовлення!\nЧек # {receipt}\nСума: {total} грн\nЧас: {time}",
        'admin_add': "➕ Додати товар",
        'admin_remove': "❌ Видалити товар",
        'admin_broadcast': "📢 Розсилка",
        'add_product_name': "Введіть назву товару:",
        'add_product_desc': "Введіть опис товару:",
        'add_product_price': "Введіть ціну товару:",
        'add_product_photo': "Введіть URL фото товару:",
        'product_added': "✅ Товар успішно додано!",
        'enter_product_id': "Введіть ID товару для видалення:",
        'product_deleted': "✅ Товар видалено!",
        'broadcast_message': "📨 Введіть повідомлення для розсилки:",
        'broadcast_sent': "✅ Розсилку завершено!",
        'invalid_price': "⚠️ Невірний формат ціни! Спробуйте ще раз:",
        'error': "🚫 Сталася помилка!",
        'invalid_id': "⚠️ Невірний формат ID!",
        'admin_menu': "🔐 Адмін-меню",
        'statistics': "📊 Статистика",
        'manage_admins': "👥 Керування адмінами",
        'view_products': "📦 Перегляд товарів",
        'main_menu': "🏠 Головне меню",
        'add_admin': "➕ Додати адміна",
        'remove_admin': "➖ Видалити адміна",
        'enter_admin_id': "Введіть ID або @username адміна:",
        'admin_added': "✅ Адміна додано!",
        'admin_removed': "✅ Адміна видалено!",
        'invalid_admin': "❌ Невірний формат адміна!",
        'total_users': "👤 Користувачів: {}",
        'total_orders': "📦 Всього замовлень: {}",
        'active_orders': "🔄 Активних замовлень: {}",
        'product_list': "📦 Список товарів:",
        'admin_panel': "🔐 Адмін-панель",
        'back_to_admin': "🔙 До адмін-меню"
    },
    'en': {
        'welcome': "Hello! Choose an action from the menu below:",
        'info': "This bot helps you order products from our catalog.",
        'catalog': "Available products:",
        'back': "🔙 Back",
        'add_to_cart': "🛒 Add to cart",
        'cart_empty': "Your cart is empty.",
        'order_name': "Enter your first name:",
        'order_lastname': "Enter your last name:",
        'order_phone': "Share your phone number:",
        'order_city': "Enter delivery city:",
        'thanks': "Thank you for your order!\nReceipt # {receipt}\nTotal: {total} UAH\nTime: {time}",
        'admin_add': "➕ Add product",
        'admin_remove': "❌ Remove product",
        'admin_broadcast': "📢 Broadcast",
        'add_product_name': "Enter product name:",
        'add_product_desc': "Enter product description:",
        'add_product_price': "Enter product price:",
        'add_product_photo': "Enter product photo URL:",
        'product_added': "✅ Product added successfully!",
        'enter_product_id': "Enter product ID to delete:",
        'product_deleted': "✅ Product deleted!",
        'broadcast_message': "📨 Enter message to broadcast:",
        'broadcast_sent': "✅ Broadcast completed!",
        'invalid_price': "⚠️ Invalid price format! Try again:",
        'error': "🚫 An error occurred!",
        'invalid_id': "⚠️ Invalid ID format!",
        'admin_menu': "🔐 Admin Menu",
        'statistics': "📊 Statistics",
        'manage_admins': "👥 Manage Admins",
        'view_products': "📦 View Products",
        'main_menu': "🏠 Main Menu",
        'add_admin': "➕ Add Admin",
        'remove_admin': "➖ Remove Admin",
        'enter_admin_id': "Enter admin ID or @username:",
        'admin_added': "✅ Admin added!",
        'admin_removed': "✅ Admin removed!",
        'invalid_admin': "❌ Invalid admin format!",
        'total_users': "👤 Total users: {}",
        'total_orders': "📦 Total orders: {}",
        'active_orders': "🔄 Active orders: {}",
        'product_list': "📦 Product list:",
        'admin_panel': "🔐 Admin Panel",
        'back_to_admin': "🔙 Back to admin menu"
    }
}


def db_connection():
    conn = sqlite3.connect('shop_bot.db')
    return conn, conn.cursor()


def initialize_db():
    conn, cursor = db_connection()
    try:
        # Создаем таблицу пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            language TEXT
        )''')

        # Создаем таблицу администраторов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE
        )''')

        # Создаем таблицу товаров
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price REAL,
            photo TEXT
        )''')

        # Создаем таблицу заказов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            city TEXT,
            items TEXT,
            total REAL,
            receipt_number TEXT,
            timestamp TEXT,
            status TEXT DEFAULT 'processing'
        )''')

        # Добавляем колонку status, если она отсутствует
        cursor.execute("PRAGMA table_info(orders)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'status' not in columns:
            cursor.execute('''
            ALTER TABLE orders 
            ADD COLUMN status TEXT DEFAULT 'processing'
            ''')

        # Добавляем администратора по умолчанию
        cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (ADMIN_ID,))

        conn.commit()

    except Exception as e:
        logging.error("Database initialization error", exc_info=True)
        conn.rollback()
    finally:
        conn.close()


def get_user_lang(user_id):
    conn, cursor = db_connection()
    cursor.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    lang = cursor.fetchone()
    conn.close()
    return lang[0] if lang else 'ua'


def is_admin(user_id):
    conn, cursor = db_connection()
    cursor.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def create_main_markup(user_id):
    lang = get_user_lang(user_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        '📋 ' + ('Каталог' if lang == 'ua' else 'Catalog'),
        '🛒 ' + ('Замовлення' if lang == 'ua' else 'Order'),
        'ℹ️ ' + ('Інфо' if lang == 'ua' else 'Info')
    ]

    if is_admin(user_id):
        buttons.append(messages['ua']['admin_menu'] if lang == 'ua' else messages['en']['admin_menu'])

    markup.add(*buttons)
    return markup


def create_admin_markup(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        messages['ua']['statistics'] if lang == 'ua' else messages['en']['statistics'],
        messages['ua']['manage_admins'] if lang == 'ua' else messages['en']['manage_admins'],
        messages['ua']['view_products'] if lang == 'ua' else messages['en']['view_products'],
        messages['ua']['admin_add'] if lang == 'ua' else messages['en']['admin_add'],
        messages['ua']['admin_remove'] if lang == 'ua' else messages['en']['admin_remove'],
        messages['ua']['admin_broadcast'] if lang == 'ua' else messages['en']['admin_broadcast'],
        messages['ua']['main_menu'] if lang == 'ua' else messages['en']['main_menu']
    ]
    markup.add(*buttons)
    return markup


def show_main_menu(message):
    lang = get_user_lang(message.from_user.id)
    bot.send_message(message.chat.id,
                     messages[lang]['welcome'],
                     reply_markup=create_main_markup(message.from_user.id))


def show_admin_menu(message):
    lang = get_user_lang(message.from_user.id)
    bot.send_message(message.chat.id,
                     messages[lang]['admin_panel'],
                     reply_markup=create_admin_markup(lang))


@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,))
        user = cursor.fetchone()

        if not user:
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_ua"),
                types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
            )
            bot.send_message(message.chat.id, "Оберіть мову / Choose language:", reply_markup=markup)
        else:
            show_main_menu(message)
    except Exception as e:
        logging.error("Error in send_welcome", exc_info=True)
    finally:
        conn.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    lang = call.data.split("_")[1]
    try:
        conn, cursor = db_connection()
        cursor.execute("INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)",
                       (call.from_user.id, lang))
        conn.commit()
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_main_menu(call.message)
    except Exception as e:
        logging.error("Error setting language", exc_info=True)
    finally:
        conn.close()


@bot.message_handler(func=lambda msg: msg.text in ['ℹ️ Інфо', 'ℹ️ Info'])
def send_info(message):
    lang = get_user_lang(message.from_user.id)
    bot.send_message(message.chat.id, messages[lang]['info'])


@bot.message_handler(func=lambda msg: msg.text in ['📋 Каталог', '📋 Catalog'])
def send_catalog(message):
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT id, name FROM products")
        products = cursor.fetchall()
        lang = get_user_lang(message.from_user.id)

        markup = types.InlineKeyboardMarkup()
        for prod in products:
            markup.add(types.InlineKeyboardButton(prod[1], callback_data=f"item_{prod[0]}"))

        markup.add(types.InlineKeyboardButton(messages[lang]['back'], callback_data="main_menu"))
        bot.send_message(message.chat.id, messages[lang]['catalog'], reply_markup=markup)
    except Exception as e:
        logging.error("Catalog error", exc_info=True)
    finally:
        conn.close()


@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def back_to_main(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_main_menu(call.message)


@bot.message_handler(func=lambda msg: msg.text in [messages['ua']['admin_menu'], messages['en']['admin_menu']])
def admin_panel(message):
    if is_admin(message.from_user.id):
        show_admin_menu(message)


@bot.message_handler(func=lambda msg: msg.text in [messages['ua']['statistics'], messages['en']['statistics']])
def show_statistics(message):
    if is_admin(message.from_user.id):
        lang = get_user_lang(message.from_user.id)
        conn, cursor = db_connection()

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'processing'")
        active_orders = cursor.fetchone()[0]

        stats = "\n".join([
            messages[lang]['total_users'].format(total_users),
            messages[lang]['total_orders'].format(total_orders),
            messages[lang]['active_orders'].format(active_orders)
        ])

        bot.send_message(message.chat.id, stats)
        conn.close()


@bot.message_handler(func=lambda msg: msg.text in [messages['ua']['view_products'], messages['en']['view_products']])
def view_products(message):
    if is_admin(message.from_user.id):
        lang = get_user_lang(message.from_user.id)
        conn, cursor = db_connection()
        cursor.execute("SELECT id, name FROM products")
        products = cursor.fetchall()
        conn.close()

        product_list = "\n".join([f"{prod[0]}: {prod[1]}" for prod in products])
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            messages[lang]['back_to_admin'],
            callback_data="admin_menu"
        ))
        bot.send_message(message.chat.id, f"{messages[lang]['product_list']}\n{product_list}", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "admin_menu")
def back_to_admin_menu(call):
    show_admin_menu(call.message)


@bot.message_handler(func=lambda msg: msg.text in [messages['ua']['manage_admins'], messages['en']['manage_admins']])
def manage_admins(message):
    if is_admin(message.from_user.id):
        lang = get_user_lang(message.from_user.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            types.KeyboardButton(messages['ua']['add_admin'] if lang == 'ua' else messages['en']['add_admin']),
            types.KeyboardButton(messages['ua']['remove_admin'] if lang == 'ua' else messages['en']['remove_admin']),
            types.KeyboardButton(messages['ua']['back_to_admin'] if lang == 'ua' else messages['en']['back_to_admin'])
        )
        bot.send_message(message.chat.id, "Оберіть дію:", reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text in [messages['ua']['add_admin'], messages['en']['add_admin']])
def add_admin_handler(message):
    if is_admin(message.from_user.id):
        lang = get_user_lang(message.from_user.id)
        bot.send_message(message.chat.id, messages[lang]['enter_admin_id'])
        bot.register_next_step_handler(message, process_add_admin)


def process_add_admin(message):
    lang = get_user_lang(message.from_user.id)
    try:
        admin_input = message.text.strip().lstrip('@')
        conn, cursor = db_connection()

        if admin_input.isdigit():
            cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (int(admin_input),))
        else:
            cursor.execute("INSERT OR IGNORE INTO admins (username) VALUES (?)", (admin_input,))

        conn.commit()
        bot.send_message(message.chat.id, messages[lang]['admin_added'])
    except Exception as e:
        logging.error("Add admin error", exc_info=True)
        bot.send_message(message.chat.id, messages[lang]['invalid_admin'])
    finally:
        conn.close()
        show_admin_menu(message)


@bot.message_handler(func=lambda msg: msg.text in [messages['ua']['remove_admin'], messages['en']['remove_admin']])
def remove_admin_handler(message):
    if is_admin(message.from_user.id):
        lang = get_user_lang(message.from_user.id)
        bot.send_message(message.chat.id, messages[lang]['enter_admin_id'])
        bot.register_next_step_handler(message, process_remove_admin)


def process_remove_admin(message):
    lang = get_user_lang(message.from_user.id)
    try:
        admin_input = message.text.strip().lstrip('@')
        conn, cursor = db_connection()

        if admin_input.isdigit():
            cursor.execute("DELETE FROM admins WHERE user_id = ?", (int(admin_input),))
        else:
            cursor.execute("DELETE FROM admins WHERE username = ?", (admin_input,))

        conn.commit()
        bot.send_message(message.chat.id, messages[lang]['admin_removed'])
    except Exception as e:
        logging.error("Remove admin error", exc_info=True)
        bot.send_message(message.chat.id, messages[lang]['error'])
    finally:
        conn.close()
        show_admin_menu(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("item_"))
def handle_item_selection(call):
    try:
        item_id = int(call.data.split("_")[1])
        conn, cursor = db_connection()
        cursor.execute("SELECT name, description, price, photo FROM products WHERE id=?", (item_id,))
        item = cursor.fetchone()
        lang = get_user_lang(call.from_user.id)

        if item:
            name, desc, price, photo = item
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(messages[lang]['add_to_cart'], callback_data=f"add_{item_id}"),
                types.InlineKeyboardButton(messages[lang]['back'], callback_data="catalog_back")
            )
            caption = f"*{name}*\n\n{desc}\n\n💰 {price} грн" if lang == 'ua' else f"*{name}*\n\n{desc}\n\n💰 {price} UAH"
            bot.send_photo(call.message.chat.id, photo=photo, caption=caption,
                           parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        logging.error("Item error", exc_info=True)
    finally:
        conn.close()


@bot.callback_query_handler(func=lambda call: call.data == "catalog_back")
def back_to_catalog(call):
    send_catalog(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def add_to_cart_handler(call):
    try:
        item_id = int(call.data.split("_")[1])
        conn, cursor = db_connection()
        cursor.execute("SELECT name, price FROM products WHERE id=?", (item_id,))
        item = cursor.fetchone()
        lang = get_user_lang(call.from_user.id)

        if item:
            user_id = call.from_user.id
            if user_id not in user_cart:
                user_cart[user_id] = []
            user_cart[user_id].append(item)
            bot.answer_callback_query(call.id,
                                      f"✅ {item[0]} " + ("додано до корзини!" if lang == 'ua' else "added to cart!"))
    except Exception as e:
        logging.error("Add to cart error", exc_info=True)
    finally:
        conn.close()


@bot.message_handler(func=lambda msg: msg.text in ['🛒 Замовлення', '🛒 Order'])
def handle_order(message):
    lang = get_user_lang(message.from_user.id)
    user_id = message.from_user.id

    if user_id not in user_cart or not user_cart[user_id]:
        bot.send_message(message.chat.id, messages[lang]['cart_empty'])
        return

    total = sum(item[1] for item in user_cart[user_id])
    order_data[user_id] = {
        'cart': user_cart[user_id],
        'total': total
    }

    bot.send_message(message.chat.id, messages[lang]['order_name'])
    bot.register_next_step_handler(message, process_order_name)


def process_order_name(message):
    lang = get_user_lang(message.from_user.id)
    user_id = message.from_user.id
    order_data[user_id]['first_name'] = message.text.strip()
    bot.send_message(message.chat.id, messages[lang]['order_lastname'])
    bot.register_next_step_handler(message, process_order_lastname)


def process_order_lastname(message):
    lang = get_user_lang(message.from_user.id)
    user_id = message.from_user.id
    order_data[user_id]['last_name'] = message.text.strip()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    contact_btn = types.KeyboardButton(
        text="📱 " + ("Надіслати контакт" if lang == 'ua' else "Share contact"),
        request_contact=True
    )
    markup.add(contact_btn)

    bot.send_message(message.chat.id, messages[lang]['order_phone'], reply_markup=markup)
    bot.register_next_step_handler(message, process_order_phone)


def process_order_phone(message):
    lang = get_user_lang(message.from_user.id)
    user_id = message.from_user.id
    if message.contact:
        order_data[user_id]['phone'] = message.contact.phone_number
    else:
        order_data[user_id]['phone'] = message.text.strip()

    bot.send_message(message.chat.id, messages[lang]['order_city'],
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_order_city)


def process_order_city(message):
    conn = None
    cursor = None
    try:
        user_id = message.from_user.id
        lang = get_user_lang(user_id)
        data = order_data[user_id]
        data['city'] = message.text.strip()

        receipt_number = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        timestamp = datetime.now().strftime("%d.%m.%Y о %H:%M")

        # Подключение к базе данных
        conn, cursor = db_connection()
        cursor.execute('''INSERT INTO orders 
                   (user_id, first_name, last_name, phone, city, items, total, receipt_number, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (user_id, data['first_name'], data['last_name'], data['phone'], data['city'],
                        str(data['cart']), data['total'], receipt_number, timestamp))
        conn.commit()

        # Generate PDF receipt
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
        pdf.set_font('DejaVu', '', 12)
        LOGO_PATH = "img/Logo.png"
        pdf.image(LOGO_PATH, x=10, y=10, w=30)

        # Формируем список товаров
        content = [
            f"{'Чек' if lang == 'ua' else 'Receipt'} #{receipt_number}",
            "-----------------------"
        ]

        # Добавляем товары из корзины (работа с кортежами)
        for index, item in enumerate(data['cart'], 1):
            product_name = item[0]  # Название товара (первый элемент кортежа)
            price = item[1]  # Цена (второй элемент кортежа)
            content.append(f"{index}. {product_name} - {price} ₴")

        content.extend([
            "-----------------------",
            f"{'ВСЬОГО' if lang == 'ua' else 'TOTAL'}: {data['total']} ₴",
            "-----------------------",
            f"{data['first_name']} {data['last_name']}",
            data['phone'],
            data['city'],
            "-----------------------",
            f"{timestamp}",
            "Бажаємо вам успіхів!" if lang == 'ua' else "Good luck!"
        ])

        # Записываем содержимое в PDF
        y_position = 45  # Стартовая позиция после логотипа
        for line in content:
            pdf.set_xy(10, y_position)
            pdf.cell(200, 10, txt=line, ln=1)
            y_position += 10

        pdf.output(f"receipt_{receipt_number}.pdf")

        # Отправляем чек пользователю
        with open(f"receipt_{receipt_number}.pdf", 'rb') as doc:
            bot.send_document(message.chat.id, doc)

        # Уведомление админу
        admin_msg = (
            f"🛒 Нове замовлення #{receipt_number}\n"
            f"👤 Клієнт: {data['first_name']} {data['last_name']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"🏙️ Місто: {data['city']}\n"
            f"💵 Сума: {data['total']} UAH"
        )
        bot.send_message(ADMIN_ID, admin_msg)

        # Очистка данных
        del user_cart[user_id]
        del order_data[user_id]

        bot.send_message(message.chat.id, messages[lang]['thanks'].format(
            receipt=receipt_number,
            total=data['total'],
            time=timestamp
        ))

    except Exception as e:
        logging.error(f"Order processing error: {str(e)}", exc_info=True)
        lang = get_user_lang(message.from_user.id)
        bot.send_message(message.chat.id, messages[lang]['error'])
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        show_main_menu(message)


@bot.message_handler(func=lambda msg: msg.text in [messages['ua']['admin_add'], messages['en']['admin_add']])
def handle_add_product(message):
    if is_admin(message.from_user.id):
        lang = get_user_lang(message.from_user.id)
        adding_product[message.from_user.id] = {}
        bot.send_message(message.chat.id, messages[lang]['add_product_name'])
        bot.register_next_step_handler(message, process_product_name)


def process_product_name(message):
    lang = get_user_lang(message.from_user.id)
    adding_product[message.from_user.id]['name'] = message.text.strip()
    bot.send_message(message.chat.id, messages[lang]['add_product_desc'])
    bot.register_next_step_handler(message, process_product_description)


def process_product_description(message):
    lang = get_user_lang(message.from_user.id)
    adding_product[message.from_user.id]['desc'] = message.text.strip()
    bot.send_message(message.chat.id, messages[lang]['add_product_price'])
    bot.register_next_step_handler(message, process_product_price)


def process_product_price(message):
    lang = get_user_lang(message.from_user.id)
    try:
        price = float(message.text.strip())
        adding_product[message.from_user.id]['price'] = price
        bot.send_message(message.chat.id, messages[lang]['add_product_photo'])
        bot.register_next_step_handler(message, process_product_photo)
    except ValueError:
        bot.send_message(message.chat.id, messages[lang]['invalid_price'])
        bot.register_next_step_handler(message, process_product_price)


def process_product_photo(message):
    lang = get_user_lang(message.from_user.id)
    try:
        product_data = adding_product[message.from_user.id]
        product_data['photo'] = message.text.strip()

        conn, cursor = db_connection()
        cursor.execute('''INSERT INTO products 
            (name, description, price, photo)
            VALUES (?, ?, ?, ?)''',
                       (product_data['name'], product_data['desc'],
                        product_data['price'], product_data['photo']))
        conn.commit()

        bot.send_message(message.chat.id, messages[lang]['product_added'])
    except Exception as e:
        logging.error("Product add error", exc_info=True)
        bot.send_message(message.chat.id, messages[lang]['error'])
    finally:
        conn.close()
        del adding_product[message.from_user.id]
        show_admin_menu(message)


@bot.message_handler(func=lambda msg: msg.text in [messages['ua']['admin_remove'], messages['en']['admin_remove']])
def handle_remove_product(message):
    if is_admin(message.from_user.id):
        lang = get_user_lang(message.from_user.id)
        bot.send_message(message.chat.id, messages[lang]['enter_product_id'])
        bot.register_next_step_handler(message, process_remove_product)


def process_remove_product(message):
    lang = get_user_lang(message.from_user.id)
    try:
        product_id = int(message.text.strip())
        conn, cursor = db_connection()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        bot.send_message(message.chat.id, messages[lang]['product_deleted'])
    except Exception as e:
        logging.error("Product remove error", exc_info=True)
        bot.send_message(message.chat.id, messages[lang]['invalid_id'])
    finally:
        conn.close()
        show_admin_menu(message)


@bot.message_handler(
    func=lambda msg: msg.text in [messages['ua']['admin_broadcast'], messages['en']['admin_broadcast']])
def handle_broadcast(message):
    if is_admin(message.from_user.id):
        lang = get_user_lang(message.from_user.id)
        bot.send_message(message.chat.id, messages[lang]['broadcast_message'])
        bot.register_next_step_handler(message, process_broadcast)


def process_broadcast(message):
    lang = get_user_lang(message.from_user.id)
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()

        for user in users:
            try:
                bot.send_message(user[0], message.text)
            except Exception as e:
                logging.error(f"Broadcast failed for user {user[0]}: {str(e)}")

        bot.send_message(message.chat.id, messages[lang]['broadcast_sent'])
    except Exception as e:
        logging.error("Broadcast error", exc_info=True)
        bot.send_message(message.chat.id, messages[lang]['error'])
    finally:
        conn.close()
        show_admin_menu(message)

if __name__ == '__main__':
    initialize_db()
    bot.polling(none_stop=True)