from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import asyncio

BOT_TOKEN = "8046271807:AAExKsEgXLkxvrEvPWTfyfMsI2OFXaTfJh4"  # твой токен
SECRET_PASSWORD = "topsecret123"  # пароль для секретного чата
authorized_users = set()  # ID пользователей, которым открыт секретный чат
user_messages = {}  # хранение сообщений для очистки

# Инициализация бота
session = AiohttpSession()
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
    session=session
)
dp = Dispatcher()

# --- Главное меню (обычная панель) ---
def main_panel():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("📊 System Logs"), KeyboardButton("👥 User Manager")],
            [KeyboardButton("🔧 Settings")]
        ],
        resize_keyboard=True
    )
    return kb

# --- Секретный чат (после ввода пароля) ---
def secret_chat_panel():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("💬 Send Message")],
            [KeyboardButton("🚪 Exit Chat")]
        ],
        resize_keyboard=True
    )
    return kb

# --- Команда старт ---
@dp.message()
async def start_handler(message: types.Message):
    if message.from_user.id not in authorized_users:
        await message.answer("Welcome to Admin Panel", reply_markup=main_panel())
    else:
        await message.answer("You are in Secret Chat", reply_markup=secret_chat_panel())

# --- Проверка пароля для доступа ---
@dp.message()
async def password_check(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    if text == SECRET_PASSWORD and user_id not in authorized_users:
        authorized_users.add(user_id)
        user_messages[user_id] = []  # создаём список сообщений для очистки
        await message.answer(
            "✅ Access Granted. Secret Chat Opened.",
            reply_markup=secret_chat_panel()
        )

# --- Обработка секретного чата ---
@dp.message()
async def secret_chat_handler(message: types.Message):
    user_id = message.from_user.id

    # Если пользователь в секретном чате
    if user_id in authorized_users:
        if message.text == "🚪 Exit Chat":
            # Выход из чата
            authorized_users.remove(user_id)
            # Удаляем все сообщения бота у пользователя
            msgs = user_messages.get(user_id, [])
            for msg_id in msgs:
                try:
                    await bot.delete_message(user_id, msg_id)
                except:
                    pass
            user_messages[user_id] = []

            await message.answer(
                "🔴 You have exited the secret chat.",
                reply_markup=ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
            )
        else:
            # Сохраняем сообщение и эмулируем отправку в секретный чат
            msg = await message.answer(f"<b>You:</b> {message.text}")
            user_messages[user_id].append(msg.message_id)

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
