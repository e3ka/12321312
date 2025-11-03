# bot_encoder.py

import base64 as _b
import marshal as _m
import zlib as _z
import hashlib as _h
import os
import platform
import sys
import telebot
from telebot import types

# --- НАСТРОЙКИ ---
BOT_TOKEN = '8125038982:AAEBb2mx9R6LG-gRzouS_4lmmY98DQsahh8'  # ЗАМЕНИТЬ НА ТОКЕН ТВОЕГО БОТА
ADMIN_USER_ID = 1232470077  # ЗАМЕНИТЬ НА ТВОЙ ЧИСЛОВОЙ TELEGRAM ID
PLUGIN_FILENAME = 'plugin.py' # Имя файла с плагином, который будет шифроваться
OUTPUT_FILENAME = 'encoded_plugin_linux_py311.py' # Имя выходного файла
# --- /НАСТРОЙКИ ---

bot = telebot.TeleBot(BOT_TOKEN)

def check_access(message):
    """Проверяет, является ли отправитель администратором."""
    if message.from_user.id != ADMIN_USER_ID:
        bot.reply_to(message, "❌ Доступ запрещён.")
        return False
    return True

def check_environment():
    """Проверяет, запущен ли скрипт на Linux и Python 3.11."""
    if platform.system() != 'Linux':
        return False, "❌ Бот работает только на Linux."
    if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
        return False, f"❌ Бот требует Python 3.11, текущая версия: {platform.python_version()}"
    return True, ""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not check_access(message):
        return

    welcome_text = (
        "🔐 Бот-шифратор плагинов (Linux + Python 3.11 ONLY)\n\n"
        "Доступные команды:\n"
        "/encode_file - Зашифровать файл plugin.py (должен быть в папке с ботом)\n"
        "/encode_text - Зашифровать код, отправленный как текстовое сообщение\n"
        "/help - Показать это сообщение"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    if not check_access(message):
        return

    help_text = (
        "🔐 Бот-шифратор плагинов (Linux + Python 3.11 ONLY)\n\n"
        "Доступные команды:\n"
        "/encode_file - Зашифровать файл plugin.py (должен быть в папке с ботом)\n"
        "/encode_text - Зашифровать код, отправленный как текстовое сообщение\n"
        "/help - Показать это сообщение\n\n"
        "⚠️ ВНИМАНИЕ: Этот бот выполняет произвольный Python-код. Используйте с осторожностью."
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['encode_file'])
def encode_from_file(message):
    if not check_access(message):
        return

    ok, error_msg = check_environment()
    if not ok:
        bot.reply_to(message, error_msg)
        return

    if not os.path.exists(PLUGIN_FILENAME):
        bot.reply_to(message, f"❌ Файл '{PLUGIN_FILENAME}' не найден в папке бота.")
        return

    try:
        with open(PLUGIN_FILENAME, 'r', encoding='utf-8') as f:
            plugin_code = f.read()
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка чтения файла: {e}")
        return

    try:
        # --- ШИФРОВАНИЕ ---
        compiled_code = _m.dumps(compile(plugin_code, PLUGIN_FILENAME, 'exec'))
        compressed_code = _z.compress(compiled_code)
        encoded_code = _b.b85encode(compressed_code).decode('utf-8')
        code_hash = _h.sha256(encoded_code.encode('utf-8')).hexdigest()

        final_code = f"""import base64 as _b,marshal as _m,zlib as _z,platform,sys; 
if platform.system() != 'Linux':
    raise RuntimeError('Плагин работает только на Linux.')
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(f'Плагин требует Python 3.11, текущая версия: {{platform.python_version()}}')
ojuawh='{encoded_code}'
import hashlib as _h
assert _h.sha256(ojuawh.encode("utf-8")).hexdigest()=='{code_hash}'
exec(_m.loads(_z.decompress(_b.b85decode(ojuawh))),globals(),globals())
"""
        # --- /ШИФРОВАНИЕ ---

        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(final_code)

        response_text = (
            "✅ Плагин успешно зашифрован и ограничен для Linux + Python 3.11!\n"
            f"📁 Создан файл: {OUTPUT_FILENAME}\n"
            f"🔐 Хеш: {code_hash}\n"
            f"📊 Размер исходного: {len(plugin_code)} символов\n"
            f"📊 Размер зашифрованного: {len(final_code)} символов\n"
            f"🎯 Совместимость: Только Linux, только Python 3.11"
        )
        bot.reply_to(message, response_text)

        # Отправляем файл
        with open(OUTPUT_FILENAME, 'rb') as f:
            bot.send_document(message.chat.id, f)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка шифрования: {e}")

@bot.message_handler(commands=['encode_text'])
def ask_for_code(message):
    if not check_access(message):
        return

    msg = bot.reply_to(message, "Отправьте Python-код, который нужно зашифровать.")
    bot.register_next_step_handler(msg, process_code_message)

def process_code_message(message):
    if not check_access(message):
        return

    ok, error_msg = check_environment()
    if not ok:
        bot.reply_to(message, error_msg)
        return

    # Получаем текст кода
    plugin_code = message.text
    if not plugin_code.strip():
        bot.reply_to(message, "❌ Код не может быть пустым.")
        return

    try:
        # --- ШИФРОВАНИЕ ---
        # Используем произвольное имя файла для компиляции
        compiled_code = _m.dumps(compile(plugin_code, '<user_input>', 'exec'))
        compressed_code = _z.compress(compiled_code)
        encoded_code = _b.b85encode(compressed_code).decode('utf-8')
        code_hash = _h.sha256(encoded_code.encode('utf-8')).hexdigest()

        final_code = f"""import base64 as _b,marshal as _m,zlib as _z,platform,sys; 
if platform.system() != 'Linux':
    raise RuntimeError('Плагин работает только на Linux.')
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(f'Плагин требует Python 3.11, текущая версия: {{platform.python_version()}}')
ojuawh='{encoded_code}'
import hashlib as _h
assert _h.sha256(ojuawh.encode("utf-8")).hexdigest()=='{code_hash}'
exec(_m.loads(_z.decompress(_b.b85decode(ojuawh))),globals(),globals())
"""
        # --- /ШИФРОВАНИЕ ---

        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(final_code)

        response_text = (
            "✅ Код успешно зашифрован и ограничен для Linux + Python 3.11!\n"
            f"📁 Создан файл: {OUTPUT_FILENAME}\n"
            f"🔐 Хеш: {code_hash}\n"
            f"📊 Размер исходного: {len(plugin_code)} символов\n"
            f"📊 Размер зашифрованного: {len(final_code)} символов\n"
            f"🎯 Совместимость: Только Linux, только Python 3.11"
        )
        bot.reply_to(message, response_text)

        # Отправляем файл
        with open(OUTPUT_FILENAME, 'rb') as f:
            bot.send_document(message.chat.id, f)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка шифрования: {e}")

if __name__ == "__main__":
    print("🔐 Бот-шифратор запущен (Linux + Python 3.11 ONLY)")
    print("=" * 50)
    ok, error_msg = check_environment()
    if not ok:
        print(error_msg)
        print("❌ Завершение работы бота.")
        exit(1)
    print(f"🤖 Бот запускается с токеном: {BOT_TOKEN[:5]}...")
    print(f"👤 Администратор: {ADMIN_USER_ID}")
    print("...")
    bot.infinity_polling(skip_pending=True)
