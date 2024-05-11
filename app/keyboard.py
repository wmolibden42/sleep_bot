from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
#кнопки, которые будут записывать время подъема/отбоя/настроение и вывод статистики
start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Подъем'),
                                      KeyboardButton(text='Отбой')],
                                      [KeyboardButton(text='Настроение')],
                                      [KeyboardButton(text='Статистика')]],
                               resize_keyboard=True,
                               input_field_placeholder='Выбери пункт меню',
                               one_time_keyboard=True)

#кнопки для ввода данных
#wake_up = InlineKeyboardMarkup(inline_keyboard=[
#    [InlineKeyboardButton(text='IWrite', callback_data='Write'), #ручной ввод данных
     #InlineKeyboardButton(text='Click', callback_data='Click')], #сохранине времени от нажати
#    [InlineKeyboardButton(text='back', callback_data='back')]]) #вернуться назад