import telebot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

SCAMMERS_FILE = "scammers.txt"
TRUSTED_FILE = "trusted.txt"

def load_list(filename):
    if not os.path.exists(filename):
        return set()
    with open(filename, "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())

def save_to_list(filename, username):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(username + "\n")

def remove_from_list(filename, username):
    if not os.path.exists(filename):
        return
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            if line.strip().lower() != username:
                f.write(line)

def refresh_lists():
    global scammer_list, trusted_list
    scammer_list = load_list(SCAMMERS_FILE)
    trusted_list = load_list(TRUSTED_FILE)

refresh_lists()

main_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("1. Список скамеров", "2. Проверенные люди")
main_menu.add("3. Я не скамер но попал в список", "4. Донат")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите раздел:", reply_markup=main_menu)

@bot.message_handler(func=lambda m: m.text == "1. Список скамеров")
def ask_scammer(message):
    msg = bot.send_message(message.chat.id, "Введите ник или ID для проверки:")
    bot.register_next_step_handler(msg, check_scammer)

def check_scammer(message):
    username = message.text.strip().lower()
    if username in scammer_list:
        bot.send_message(message.chat.id, "⚠️ Этот пользователь в списке скамеров.")
    else:
        bot.send_message(message.chat.id, "✅ Пользователь не найден в списке скамеров.")

@bot.message_handler(func=lambda m: m.text == "2. Проверенные люди")
def ask_trusted(message):
    msg = bot.send_message(message.chat.id, "Введите ник или ID человека, которого хотите проверить:")
    bot.register_next_step_handler(msg, check_trusted)

def check_trusted(message):
    username = message.text.strip().lower()
    if username in trusted_list:
        bot.send_message(message.chat.id, "✅ Этот человек в списке проверенных.")
    else:
        bot.send_message(message.chat.id, "❌ Этого человека нет в списке проверенных.")

@bot.message_handler(func=lambda m: m.text == "3. Я не скамер но попал в список")
def not_scammer_request(message):
    username = message.from_user.username or f"id {message.from_user.id}"
    msg = f"⚠️ Запрос на пересмотр: пользователь @{username} считает, что он попал в список скамеров по ошибке."
    bot.send_message(OWNER_ID, msg)
    bot.send_message(message.chat.id, "Ваш запрос отправлен. Мы рассмотрим его в ближайшее время.")

@bot.message_handler(func=lambda m: m.text == "4. Донат")
def donate_info(message):
    bot.send_message(message.chat.id,
        "Хочешь поддержать проект?\n"
        "Мой ник в Roblox: *@RatatouyVO*\n"
        "Можешь поддержать звёздочками в Telegram или робуксами!",
        parse_mode="Markdown")

@bot.message_handler(commands=['add_scammer'])
def add_scammer(message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используй так: /add_scammer username_or_id")
        return
    username = parts[1].strip().lower()
    if username in scammer_list:
        bot.reply_to(message, "Этот пользователь уже есть в списке скамеров.")
        return
    save_to_list(SCAMMERS_FILE, username)
    refresh_lists()
    bot.reply_to(message, f"Пользователь {username} добавлен в список скамеров.")

@bot.message_handler(commands=['remove_scammer'])
def remove_scammer(message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используй так: /remove_scammer username_or_id")
        return
    username = parts[1].strip().lower()
    if username not in scammer_list:
        bot.reply_to(message, "Пользователя нет в списке скамеров.")
        return
    remove_from_list(SCAMMERS_FILE, username)
    refresh_lists()
    bot.reply_to(message, f"Пользователь {username} удалён из списка скамеров.")

@bot.message_handler(commands=['add_trusted'])
def add_trusted(message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используй так: /add_trusted username_or_id")
        return
    username = parts[1].strip().lower()
    if username in trusted_list:
        bot.reply_to(message, "Этот пользователь уже есть в списке проверенных.")
        return
    save_to_list(TRUSTED_FILE, username)
    refresh_lists()
    bot.reply_to(message, f"Пользователь {username} добавлен в список проверенных.")

@bot.message_handler(commands=['remove_trusted'])
def remove_trusted(message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используй так: /remove_trusted username_or_id")
        return
    username = parts[1].strip().lower()
    if username not in trusted_list:
        bot.reply_to(message,"Пользователя нет в списке проверенных людей. ")
        return
    remove_from_list(TRUSTED_FILE, username)
    refresh_lists()
    bot.reply_to(message, f"Пользователь {username} удалён из списка проверенных.")

bot.polling(none_stop=True)
