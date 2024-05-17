from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
#кнопки, которые будут записывать время подъема/отбоя/настроение и вывод статистики
start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Начать')],
#                                      KeyboardButton(text='Ввести в ручную')],
                                      [KeyboardButton(text='Статистика')]],
                               resize_keyboard=True,
                               input_field_placeholder='Выбери пункт меню',
                               one_time_keyboard=True)

wake_up = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Написать', callback_data='up_write'), #ручной ввод данных
     InlineKeyboardButton(text='Нажать утром', callback_data='up_click')], #сохранине времени от нажати
    [InlineKeyboardButton(text='Вернуться назад', callback_data='up_back')]]) #вернуться назад


click_up = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Я проснулся!', callback_data='click_click')],
    [InlineKeyboardButton(text='Вернуться назад', callback_data='click_back')]
])

down_up = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Написать', callback_data='down_write'), #ручной ввод данных
     InlineKeyboardButton(text='Нажать перед сном', callback_data='down_click')], #сохранине времени от нажати
    [InlineKeyboardButton(text='Вернуться назад', callback_data='down_back')]]) #вернуться назад

click_down = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ложусь спать!', callback_data='d_click')],
    [InlineKeyboardButton(text='Вернуться назад', callback_data='d_back')]
])

how_you = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1', callback_data='h_one'),
     InlineKeyboardButton(text='2', callback_data='h_two'),
     InlineKeyboardButton(text='3', callback_data='h_three'),
     InlineKeyboardButton(text='4', callback_data='h_four'),
     InlineKeyboardButton(text='5', callback_data='h_five')],
    [InlineKeyboardButton(text='6', callback_data='h_six'),
     InlineKeyboardButton(text='7', callback_data='h_seven'),
     InlineKeyboardButton(text='8', callback_data='h_eight'),
     InlineKeyboardButton(text='9', callback_data='h_nine'),
     InlineKeyboardButton(text='10', callback_data='h_ten')]
])

how_you_night = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1', callback_data='n_one'),
     InlineKeyboardButton(text='2', callback_data='n_two'),
     InlineKeyboardButton(text='3', callback_data='n_three'),
     InlineKeyboardButton(text='4', callback_data='n_four'),
     InlineKeyboardButton(text='5', callback_data='n_five')],
    [InlineKeyboardButton(text='6', callback_data='n_six'),
     InlineKeyboardButton(text='7', callback_data='n_seven'),
     InlineKeyboardButton(text='8', callback_data='n_eight'),
     InlineKeyboardButton(text='9', callback_data='n_nine'),
     InlineKeyboardButton(text='10', callback_data='n_ten')]
])

clack = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Хочу спать!', callback_data='clack_clack')],
    [InlineKeyboardButton(text='Вернуться назад', callback_data='clack_back')]
])