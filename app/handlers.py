from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from app import keyboard as kb

r = Router()

class Write(StatesGroup):
    wake_up = State()
    wake_down = State()
    how_you = State()

@r.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}!", reply_markup=kb.start_kb)

@r.message(F.text=='Подъем') #если пользователь хочет записать подъем
async def wake_up(message: Message, state: FSMContext):
    await state.set_state(Write.wake_up)
    await message.answer('Напиши время своего пробуждения, а я запомню!')

@r.message(Write.wake_up)
async def wake_up_st(message: Message, state: FSMContext):
    await state.update_data(wake_up=message.text)
    #wake_up = await state.get_data()
    await state.clear()

@r.message(F.text=='Отбой')
async def wake_dw(message: Message, state: FSMContext):
    await state.set_state(Write.wake_down)
    await message.answer('Напиши время, когда сегодня заснула, а я запомню')

@r.message(Write.wake_down)
async def wake_down_st(message: Message, state: FSMContext):
    await state.update_data(wake_down=message.text)
    await state.clear()
@r.message(F.text=='Настроение')
async def how_you(msg: Message, state: FSMContext):
    await state.set_state(Write.how_you)
    await msg.answer('Как ты оценишь свое настроение за день?')

@r.message(Write.how_you)
async def how_you_state(msg: Message, state: FSMContext):
    await state.update_data(how_you=msg.text)
    await state.clear()



#@r.callback_query(F.data=='Write') #обязательно добавить машину состояний
#async def cal_wake(call: CallbackQuery):
 #   await call.mmessage.answer("Напиши время подъема:")

@r.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")