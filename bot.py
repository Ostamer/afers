import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram.client.session.aiohttp import AiohttpSession
import g4f  # Импорт библиотеки g4f

# Токен бота
API_TOKEN = "7995383804:AAHtgOCMTsbuaMwKkLo_Sk_fTIMCvCptDj0"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, session=AiohttpSession())
dp = Dispatcher(storage=MemoryStorage())

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Справочник"), KeyboardButton(text="Проверка сайта")],
        [KeyboardButton(text="Дать совет"), KeyboardButton(text="Тест на схемы мошенничества")],
    ],
    resize_keyboard=True
)

# Состояния для FSM
class AdviceState(StatesGroup):
    waiting_for_problem = State()

# Хендлер команды /start
@dp.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer("Привет! Чем могу помочь?", reply_markup=main_menu)

# Хендлер для "Справочник"
@dp.message(F.text == "Справочник")
async def reference_info(message: types.Message):
    await message.answer("Справочная информация")

# Хендлер для "Проверка сайта"
@dp.message(F.text == "Проверка сайта")
async def check_website(message: types.Message):
    await message.answer("Введите url сайта:")

# Хендлер для "Дать совет"
@dp.message(F.text == "Дать совет")
async def give_advice(message: types.Message, state: FSMContext):
    await message.answer("Опишите свою ситуацию:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdviceState.waiting_for_problem)

# Хендлер для обработки текста проблемы
@dp.message(AdviceState.waiting_for_problem)
async def process_problem(message: types.Message, state: FSMContext):
    user_problem = message.text
    await message.answer("Обрабатываю ваш запрос...")

    # Отправляем запрос в g4f
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": user_problem}],
        )
        bot_reply = response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Ошибка при работе с g4f: {e}")
        bot_reply = "Произошла ошибка при обработке вашего запроса. Попробуйте позже."

    # Отправляем ответ пользователю
    await message.answer(bot_reply, reply_markup=main_menu)
    await state.clear()

# Хендлер для "Тест на схемы мошенничества"
@dp.message(F.text == "Тест на схемы мошенничества")
async def fraud_test(message: types.Message):
    await message.answer("Начало теста")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
