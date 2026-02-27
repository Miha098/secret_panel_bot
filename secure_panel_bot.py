import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ====== НАСТРОЙКИ ======
BOT_TOKEN = "8046271807:AAExKsEgXLkxvrEvPWTfyfMsI2OFXaTfJh4"  # твой токен
SECRET_PASSWORD = "1234"  # пароль для секретного чата
SECRET_CHAT_USER_ID = 8144329668  # твой Telegram ID (куда пересылать сообщения)
# =======================

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# FSM для мини-APP
class SecretChat(StatesGroup):
    chatting = State()

# =======================

# Кнопки панели админа
def main_panel():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("📊 System Logs"),
        KeyboardButton("👥 User Manager"),
        KeyboardButton("🔑 Enter Secret Chat")
    )
    return kb

# Кнопки мини-APP (секретного чата)
def secret_chat_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("🚪 Exit Chat")
    )
    return kb

# =======================
# Старт бота
@dp.message(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Welcome to Admin Panel", reply_markup=main_panel())

# Обработка кнопок главной панели
@dp.message()
async def main_panel_handler(message: types.Message, state: FSMContext):
    if message.text == "🔑 Enter Secret Chat":
        await message.answer("Введите пароль:", reply_markup=ReplyKeyboardRemove())
        await state.set_state("waiting_password")
    else:
        await message.answer(f"You clicked: {message.text}")

# Проверка пароля
@dp.message()
async def password_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == "waiting_password":
        if message.text == SECRET_PASSWORD:
            await message.answer("🔒 Секретный чат открыт!", reply_markup=secret_chat_kb())
            await state.set_state(SecretChat.chatting)
        else:
            await message.answer("❌ Неверный пароль!", reply_markup=main_panel())
            await state.clear()

# Секретный чат
@dp.message()
async def secret_chat_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == SecretChat.chatting:
        if message.text == "🚪 Exit Chat":
            await message.answer("Вы вышли из секретного чата.", reply_markup=main_panel())
            await state.clear()
        else:
            # Пересылаем сообщение в приватный чат
            await bot.send_message(chat_id=SECRET_CHAT_USER_ID,
                                   text=f"💬 {message.from_user.first_name}: {message.text}")
            await message.answer("✅ Сообщение отправлено!", reply_markup=secret_chat_kb())

# =======================
# Запуск
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен...")
    asyncio.run(dp.start_polling(bot))
