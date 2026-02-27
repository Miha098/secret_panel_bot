import asyncio
import os
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8046271807:AAExKsEgXLkxvrEvPWTfyfMsI2OFXaTfJh4"
ROOT_ID = 8144329668
USER_ID = 222222222  # <-- замени на ID девушки
DB_FILE = "secure_chat.db"
# =============================================

# ================= ИНИЦИАЛИЗАЦИЯ БОТА =================
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

authorized_users = set()
waiting_for_new_password = False
waiting_for_self_destruct = False

# ================= БАЗА ДАННЫХ =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            text TEXT,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("SELECT value FROM settings WHERE key='password'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ("password", "ERROR_451X")
        )
    conn.commit()
    conn.close()

def save_message(sender_id, text):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (sender_id, text, timestamp) VALUES (?, ?, ?)",
        (sender_id, text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def save_system_log(text):
    save_message(0, text)

def get_password():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key='password'")
    result = cursor.fetchone()
    conn.close()
    return result[0]

def set_password(new_password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE settings SET value=? WHERE key='password'",
        (new_password,)
    )
    conn.commit()
    conn.close()

# ================= КЛАВИАТУРЫ (ПЛИТКАМИ) =================
def main_panel():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("📊 System Logs"),
        KeyboardButton("👥 User Manager"),
        KeyboardButton("🔍 Error Scanner"),
        KeyboardButton("🛡 Security")
    )
    return kb

def root_panel():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("🔑 Change Password"),
        KeyboardButton("💣 SELF-DESTRUCT")
    )
    return kb

# ================= СТАРТ =================
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    if message.from_user.id not in [ROOT_ID, USER_ID]:
        return
    await message.answer(
        "🖥 <b>Server Control Panel v4.2</b>",
        reply_markup=main_panel()
    )

# ================= ERROR SCANNER =================
@dp.message(lambda m: m.text == "🔍 Error Scanner")
async def error_scanner(message: types.Message):
    if message.from_user.id not in [ROOT_ID, USER_ID]:
        return
    await message.answer("Enter error code:")

# ================= ОСНОВНАЯ ЛОГИКА =================
@dp.message()
async def main_handler(message: types.Message):
    global waiting_for_new_password
    global waiting_for_self_destruct

    user_id = message.from_user.id
    if user_id not in [ROOT_ID, USER_ID]:
        return

    current_password = get_password()

    # ===== ВХОД В СЕКРЕТНЫЙ ЧАТ =====
    if message.text == current_password:
        authorized_users.add(user_id)
        role = "ROOT 👑" if user_id == ROOT_ID else "USER 👤"
        save_system_log(f"SYSTEM: {role} entered secure channel")
        await message.answer(f"🟢 Secure channel established.\nAccess level: {role}")
        if user_id == ROOT_ID:
            await message.answer("ROOT controls activated.", reply_markup=root_panel())
        return

    # ===== СМЕНА ПАРОЛЯ =====
    if message.text == "🔑 Change Password" and user_id == ROOT_ID:
        waiting_for_new_password = True
        await message.answer("Enter new password:")
        return
    if waiting_for_new_password and user_id == ROOT_ID:
        set_password(message.text)
        save_system_log("SYSTEM: Password changed by ROOT")
        waiting_for_new_password = False
        await message.answer("🔐 Password updated successfully.")
        return

    # ===== SELF-DESTRUCT =====
    if message.text == "💣 SELF-DESTRUCT" and user_id == ROOT_ID:
        waiting_for_self_destruct = True
        await message.answer(
            "⚠ WARNING\nType CONFIRM_ERASE to permanently delete all data."
        )
        return
    if waiting_for_self_destruct and message.text == "CONFIRM_ERASE" and user_id == ROOT_ID:
        save_system_log("SYSTEM: Self-destruct initiated by ROOT")
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        await message.answer("💥 Data purge complete.\nSystem shutting down...")
        await bot.session.close()
        os._exit(0)

    # ===== СЕКРЕТНЫЙ ЧАТ =====
    if user_id in authorized_users:
        save_message(user_id, message.text)
        partner_id = USER_ID if user_id == ROOT_ID else ROOT_ID
        await bot.send_chat_action(partner_id, "typing")
        await asyncio.sleep(1)
        await bot.send_message(partner_id, message.text)

# ================= ЗАПУСК =================
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
