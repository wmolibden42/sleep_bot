import re
from datetime import datetime

import pytz
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from app import keyboard as kb
import db.engine as rq

# Замените 'Europe/Moscow' на ваш часовой пояс
moscow_tz = pytz.timezone('Europe/Moscow')

r = Router()

class Write(StatesGroup):
    wake_up = State()
    wake_down = State()
    how_morning = State()
    how_night = State()
class Click(StatesGroup):
    wake_up = State()
    wake_down = State()

@r.message(CommandStart( ))
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await rq.set_user(message.from_user.id)
    await message.answer(
        f"Привет, {hbold(message.from_user.full_name)}!\nТеперь я твой помощник! Надеюсь, я смогу помочь тебе надладить сон!\nПросто записывай регулярно время своего подъема и отбоя, а я буду считать эти вычисления :)", reply_markup=kb.start_kb)

@r.message(F.text=='Начать') #если пользователь хочет записать подъем
async def wake_up(message: Message, state: FSMContext):
    await message.answer(
        f'Как ты хочешь ввести данные о подъёме сегодня?\nТы можешь зафиксировать их в ручную, а можешь утром просто нажать кнопку при пробуждении',
    reply_markup=kb.wake_up)

@r.callback_query(lambda c: c.data and c.data.startswith('up')) #обработка ответа с инлайн клавиатуры
async def wake_up_st(call: CallbackQuery, state: FSMContext):
    code = call.data
    if code == 'up_write': #если захочет написать время, то нужно спросить и задать состояние
        await call.message.edit_text('Введите время подъема сегодня в формате ЧЧ:ММ:')
        await state.set_state(Write.wake_up)
    elif code == 'up_click':
        await state.set_state(Click.wake_up)
        await call.message.delete()
        await call.message.answer('Нажми на кнопку утром, когда проснешься и я запишу время подъёма сам :)', reply_markup=kb.click_up)
    elif code == 'up_back':
        await state.clear()
        await call.message.answer('И снова привет!', reply_markup=kb.start_kb)
    await call.answer()

@r.message(F.text.regexp(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'), Write.wake_up) #если пользователь записывает время в ручную, то поймается тут
async def wake_up_st(msg: Message, state: FSMContext):
    await state.update_data(up=msg.text)
    up = await state.get_data()
    await msg.reply(f'Отлично! \nЯ запомнил твой подъем в {up["up"]} :)\nКак ты оценишь свое настроение утром?', reply_markup=kb.how_you)
    await rq.set_up(up=msg.text, tg_id=msg.from_user.id)
    await state.set_state(Write.how_morning)

@r.message(Write.wake_up)
async def wake_up_els(message: Message, state: FSMContext):
    await message.reply('Введи время в корректном формате ЧЧ:ММ еще раз:')

@r.message(Write.how_morning)
async def how_you_state(msg: Message, state: FSMContext):
    await state.update_data(how_morning=msg.text)
    how = await state.get_data()
    await state.clear()
    await msg.answer('Отлично!\n Я запомнил, что сейчас ты чувствуешь!\nНажми на меня ближе ко сну! :)', reply_markup=kb.clack)
    await rq.set_how(how_morning=msg.text, tg_id=msg.from_user.id)
    await msg.answer.delete()

@r.message(Write.how_night)
async def how_you_state(msg: Message, state: FSMContext):
    await state.update_data(how_night=msg.text)
    how_night = await state.get_data()
    await state.clear()
    await msg.answer('Отлично!\n Я запомнил, что сейчас ты чувствуешь!\n', reply_markup=kb.clack)
    await rq.set_how(how_night=msg.text, tg_id=msg.from_user.id)
    await msg.answer.delete()

@r.callback_query(lambda c: c.data and c.data.startswith('clack'))
async def clack_down(call: CallbackQuery, state: FSMContext):
    code = call.data
    if code == 'clack_clack':
        await call.message.edit_text('Отлично! Я рад, что ты уже готовишься ко сну!\nКак ты оцениваешь свое настроение за день?', reply_markup=kb.how_you_night)
        await state.set_state(Write.how_night)
    if code == 'clack_back':
        await state.clear()
        await call.message.answer('И снова привет!', reply_markup=kb.start_kb)
        await call.message.delete()


@r.callback_query(lambda c: c.data and c.data.startswith('down')) #обработка ответа с инлайн клавиатуры
async def wake_up_st(call: CallbackQuery, state: FSMContext):
    code = call.data
    if code == 'down_write': #если захочет написать время, то нужно спросить и задать статус
        await call.message.edit_text('Введите время отбоя:')
        await state.set_state(Write.wake_down)
    elif code == 'down_click':
        await state.set_state(Click.wake_down)
        await call.message.delete()
        await call.message.answer('Нажми на кнопку перед тем, как заснуть и я сам запомню время твоего отхода ко сну! :)', reply_markup=kb.click_down)
    elif code == 'down_back':
        await state.clear()
        await call.message.delete()
        await call.message.answer('И снова привет!', reply_markup=kb.start_kb)
    await call.answer()

@r.callback_query(lambda c: c.data and c.data.startswith('h'))
async def howyoum_st(call: CallbackQuery, state: FSMContext):
    code = call.data
    if code == 'h_one':
        user_input = 1
        await rq.set_how_morning(input_user=user_input, tg_id=call.from_user.id)
        await call.message.answer('Мне жаль, что твое настроение такое...!\n Подумай, что ты можешь сделать для себя!!\nВернись ко мне вечером и перед тем, как убрать телефон :)',
                     reply_markup=kb.clack)
        await state.set_state(Click.wake_down)
        await call.message.delete()
    elif code == 'h_two':
        user_input = 2
        await rq.set_how_morning(input_user=user_input, tg_id=call.from_user.id)
        await state.clear()
        await call.message.answer(
            'Оу... Какая низкая оценка!\nЧто ты можешь сделать для себя?!\nВозвращайся вечером, перед тем, как убрать телефон :)',
            reply_markup=kb.clack)
        await call.message.delete()
    elif code == 'h_three':
        user_input = 3
        await rq.set_how_morning(input_user=user_input, tg_id=call.from_user.id)
        await call.message.answer(
            'Что ж.. Не все так плохо!\nПопробуй хорошо провести этот день и возвращайся вечером!\nНажми на кнопку, перед тем, как убрать телефон :)',
            reply_markup=kb.clack)
        await state.set_state(Click.wake_down)
        await call.message.delete()
    elif code == 'h_four':
        user_input = 4
        await rq.set_how_morning(input_user=user_input, tg_id=call.from_user.id)
        await call.message.answer(
            'Доброе утро, друг!!\n Я запомнил, что сейчас ты чувствуешь!\nНажми на кнопку вечером, перед тем, как убрать телефон :)',
            reply_markup=kb.clack)
        await state.set_state(Click.wake_down)
        await call.message.delete()
    elif code == 'h_five':
        user_input = 5
        await rq.set_how_morning(input_user=user_input, tg_id=call.from_user.id)
        await call.message.answer(
            'Отлично!\nЗолотая середина! Порадуй себя сегодня чем-нибудь и возвращайся вечером!\nНажми на кнопку, перед тем, как убрать телефон :)',
            reply_markup=kb.clack)
        await state.set_state(Click.wake_down)
    elif code == 'h_six':
        user_input = 6
        await rq.set_how_morning(input_user=user_input, tg_id=call.from_user.id)
        await call.message.answer(
            'Отлично! Это выше среднего!\n Я запомнил, что сейчас ты чувствуешь!\nНажми на кнопку, перед тем, как убрать телефон :)',
            reply_markup=kb.clack)
        await state.set_state(Click.wake_down)
        await call.message.delete()
    elif code == 'h_seven':
        user_input = 7
        await rq.set_how_morning(input_user=user_input, tg_id=call.from_user.id)
        await call.message.answer(
            'Отлично!\n Я запомнил, что сейчас ты чувствуешь!\nНажми на кнопку, перед тем, как убрать телефон :)',
            reply_markup=kb.clack)
        await state.set_state(Click.wake_down)
        await call.message.delete()
    elif code == 'h_eight':
        user_input = 8
        await rq.set_how_morning(input_user=user_input, tg_id=call.from_user.id)
        await call.message.answer(
            'Отлично! Это очень уверенная оценка!\n Я запомнил, что сейчас ты чувствуешь!\nНажми на кнопку, перед тем, как убрать телефон :)',
            reply_markup=kb.clack)
        await state.set_state(Click.wake_down)
        await call.message.delete()
    elif code == 'h_nine':
        user_input = 9
        await rq.set_how_morning(input_user=user_input, tg_id=call.from_user.id)
        await call.message.answer(
            'Отлично! Я рад твоему настроению :)\nПроживи этот день как следует :)\nНажми на кнопку, перед тем, как убрать телефон :)',
            reply_markup=kb.clack)
        await state.set_state(Click.wake_down)
        await call.message.delete()
    elif code == 'h_ten':
        user_input = 10
        await rq.set_how_morning(input_user=user_input, tg_id=call.from_user.id)
        await call.message.answer(
            'Отлично!\n Я запомнил, что сейчас ты чувствуешь!\nНажми на кнопку, перед тем, как убрать телефон :)',
            reply_markup=kb.clack)
        await state.set_state(Click.wake_down)
        await call.message.delete()

@r.callback_query(lambda c: c.data and c.data.startswith('n'))
async def howyoum_st(call: CallbackQuery, state: FSMContext):
    code = call.data
    if code == 'n_one':
        user_input = 1
        await rq.set_how_night(input_user=user_input, tg_id=call.from_user.id)
        await state.set_state(Click.wake_up)
        await call.message.answer('Мне жаль, что твое настроение такое...!\n Подумай, что ты можешь сделать для себя!!\nВернись ко мне вечером и перед тем, как убрать телефон :)',
                     reply_markup=kb.click_up)
        await call.message.delete()
    elif code == 'n_two':
        user_input = 2
        await rq.set_how_night(input_user=user_input, tg_id=call.from_user.id)
        await state.set_state(Click.wake_up)
        await call.message.answer(
            'Мне жаль, что твой день прошел так!\nЗавтра будет новый день!\nНажми на меня, как проснешься!',
            reply_markup=kb.click_up)
        await call.message.delete()
    elif code == 'n_three':
        user_input = 3
        await rq.set_how_night(input_user=user_input, tg_id=call.from_user.id)
        await state.set_state(Click.wake_up)
        await call.message.answer(
            'Мне жаль, что твое настроение такое...!\nВсе обязательно будет хорошо!\nНажми на меня, как проснешься!',
            reply_markup=kb.click_up)
        await call.message.delete()
    elif code == 'n_four':
        user_input = 4
        await rq.set_how_night(input_user=user_input, tg_id=call.from_user.id)
        await state.set_state(Click.wake_up)
        await call.message.answer(
            'Это весьма неплохой день!\nВозвращайся утром :)',
            reply_markup=kb.click_up)
        await call.message.delete()
    elif code == 'n_five':
        user_input = 5
        await rq.set_how_night(input_user=user_input, tg_id=call.from_user.id)
        await state.clear()
        await call.message.answer(
            'Золотая середина!\n Засыпай скорее!',
            reply_markup=kb.click_up)
        await call.message.delete()
    elif code == 'n_six':
        user_input = 6
        await rq.set_how_night(input_user=user_input, tg_id=call.from_user.id)
        await state.set_state(Click.wake_up)
        await call.message.answer(
            'Завтра будет еще день :)\n Не останавливайся на достигнутом!\nДобрых снов!',
            reply_markup=kb.click_up)
        await call.message.delete()
    elif code == 'n_seven':
        user_input = 7
        await rq.set_how_night(input_user=user_input, tg_id=call.from_user.id)
        await state.set_state(Click.wake_up)
        await call.message.delete()
        await call.message.answer(
            'Хороший день, правда? \nПриятных снов! Возвращайся завтра!)',
            reply_markup=kb.click_up)
    elif code == 'n_eight':
        user_input = 8
        await rq.set_how_night(input_user=user_input, tg_id=call.from_user.id)
        await state.set_state(Click.wake_up)
        await call.message.answer(
            'Отлично!\n Засыпай и восстанавливай силы! Завтра будет хороший день!',
            reply_markup=kb.click_up)
        await call.message.delete()
    elif code == 'n_nine':
        user_input = 9
        await rq.set_how_night(input_user=user_input, tg_id=call.from_user.id)
        await state.set_state(Click.wake_up)
        await call.message.answer(
            'Супер!\n  Высыпайся!:)',
            reply_markup=kb.click_up)
        await call.message.delete()
    elif code == 'n_ten':
        user_input = 10
        await rq.set_how_night(input_user=user_input, tg_id=call.from_user.id)
        await state.set_state(Click.wake_up)
        await call.message.answer(
            'Это прекрасные новости!\n Не забывай нажать кнопочку утром!',
            reply_markup=kb.click_up)
        await call.message.delete()

@r.callback_query(lambda c: c.data == 'd_click' or c.data == 'd_back', Click.wake_down)
async def process_click_up_callback(call: CallbackQuery, state: FSMContext):
    if call.data == 'd_click':
        click_time_utc = call.message.date
        # Конвертируем время в локальный часовой пояс
        click_time_local = click_time_utc.replace(tzinfo=pytz.utc).astimezone(moscow_tz)
        # Вызываем функцию set_up, передавая скорректированное время
        await rq.click_set_down(click_time_local, call.from_user.id)
        # Отправка сообщения пользователю с локальным временем
        await call.message.delete()
        await call.message.answer(
            f'Приятных снов!\nВремя отбоя {click_time_local.strftime("%H:%M:%S")} сохранено!\nНе забывай обо мне утром!', reply_markup=kb.click_up)
        # await state.clear()
        await state.set_state(Click.wake_up)
    elif call.data == 'd_back':
        # Возвращаем пользователя в главное меню
        await state.clear()
        await call.message.answer('И снова привет!', reply_markup=kb.start_kb)
        await call.message.delete()
    await call.answer()

@r.message(F.text.regexp(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'), Write.wake_down)
async def wake_down_st(message: Message, state: FSMContext):
    await state.update_data(wake_down=message.text)
    wake_down = await state.get_data()
    await state.clear()
    await message.delete()
    await message.answer(f'Отлично!\nЯ запомнил время твоего отбоя в {wake_down["wake_down"]}\nНе забывай обо мне утром!', reply_markup=kb.start_kb)
    await rq.set_down(down=message.text, tg_id=message.from_user.id)

@r.message(Write.wake_down)
async def wake_up_els(message: Message, state: FSMContext):
    await message.reply('Введи время в корректном формате ЧЧ:ММ еще раз:')

# Обработчик колбеков от кнопок click_up
@r.callback_query(lambda c: c.data == 'click_click' or c.data == 'click_back', Click.wake_up)
async def process_click_up_callback(call: CallbackQuery, state: FSMContext):
    if call.data == 'click_click':
        click_time_utc = call.message.date
        # Конвертируем время в локальный часовой пояс
        click_time_local = click_time_utc.replace(tzinfo=pytz.utc).astimezone(moscow_tz)
        # Вызываем функцию set_up, передавая скорректированное время
        await rq.click_set_up(click_time_local, call.from_user.id)
        await call.message.delete()
        # Отправка сообщения пользователю с локальным временем
        await call.message.answer(
            f'Доброе утро!\nВремя подъёма {click_time_local.strftime("%H:%M:%S")} сохранено!\nКак ты себя сейчас чувствуешь?', reply_markup=kb.how_you)
        # await state.clear()
    elif call.data == 'click_back':
        # Возвращаем пользователя в главное меню
        await state.clear()
        await call.message.answer('И снова привет!', reply_markup=kb.start_kb)
        await call.message.delete()
    await call.answer()

@r.message(F.text == "Статистика")
async def how_you(msg: Message):
    await rq.calculate_sleep_amount(tg_id=msg.from_user.id)
    answers = await rq.fetch_all(tg_id=msg.from_user.id)
    response_message = ""  # Инициализация пустой строки для сбора ответов

    for answer in answers:
        # Убедитесь, что у объектов 'answer' есть атрибут 'created'
        formatted_date = answer.created.strftime("%d %B %Y года")
        # Добавление информации о каждом ответе в общую строку
        response_message += f"Дата: {formatted_date},  Количество сна: {answer.amount}\n Утро: Время: {answer.up}, Настроение: {answer.how_morning};\n Вечер: {answer.down}, Настроение: {answer.how_night}\n\n"
    # Отправка собранного сообщения
    await msg.answer(response_message, reply_markup=kb.start_kb)

@r.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.answer("Прости, я не знаю такого. Попробуй воспользоваться кнопками! :)")
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")