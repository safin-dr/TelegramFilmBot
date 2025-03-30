from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

main: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Поиск фильма, сериала')],
              [KeyboardButton(text='Моя история'), KeyboardButton(text='Моя статистика')],
              [KeyboardButton(text='Помощь')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите интересующую опцию'
)

help_buttons: InlineKeyboardButton = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Найти кино по запросу 🫡', callback_data='search')],
                     [InlineKeyboardButton(text='Показать мою историю 🙊', callback_data='history')],
                     [InlineKeyboardButton(text='Показать мою статистику 🧐', callback_data='stats')]]
)
