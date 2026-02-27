from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- Настройки бота ---
BOT_TOKEN = "ВАШ_ТОКЕН"
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- FSM для мини-APP ---
class MiniApp(StatesGroup):
    waiting_for_password = State()
    in_secret_chat = State()

# --- Клавиатура для мини-APP ---
def secret_panel_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💬 Написать сообщение"))
    kb.add(KeyboardButton("🚪 Выйти из чата"))
    return kb

# --- Команда /start ---
@dp.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    await message.answer("Привет! Введите пароль для доступа к секретному чату.")
    await state.set_state(MiniApp.waiting_for_password)

# --- Ввод пароля ---
PASSWORD = "1234"  # Здесь можно свой пароль

@dp.message(MiniApp.waiting_for_password)
async def password_handler(message: Message, state: FSMContext):
    if message.text == PASSWORD:
        await message.answer(
            "Пароль принят! Добро пожаловать в секретный чат.", 
            reply_markup=secret_panel_keyboard()
        )
        await state.set_state(MiniApp.in_secret_chat)
    else:
        await message.answer("Неверный пароль. Попробуйте снова.")

# --- Работа в мини-APP ---
@dp.message(MiniApp.in_secret_chat)
async def secret_chat_handler(message: Message, state: FSMContext):
    if message.text == "🚪 Выйти из чата":
        await state.clear()  # Очистка состояния
        await message.answer("Вы вышли из секретного чата. История удалена ✅", reply_markup=None)
    else:
        # Здесь можно обрабатывать сообщения, например логировать или пересылать куда-то
        await message.answer(f"Вы написали: {message.text}")

# --- Запуск бота ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
