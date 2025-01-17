import os
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

load_dotenv()

authorization_link = os.getenv('LINK_APP_HH')


def menu():
    button_link = [
        [InlineKeyboardButton(text="📖 Как пользоваться", callback_data='information')],
        [InlineKeyboardButton(text='Авторизация через HH', url=authorization_link)],
        [InlineKeyboardButton(text='WEB Авторизация через HH', web_app=WebAppInfo(url=authorization_link))],
        [InlineKeyboardButton(text='Заполнить данные для отклика', callback_data='fill_data')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=button_link)


def authorized_user_menu():
    user_menu = [
        [InlineKeyboardButton(text="📖 Как пользоваться", callback_data='information')],
        [InlineKeyboardButton(text='👤 Управлять профилем', callback_data='profile_keyboard')],
        [InlineKeyboardButton(text="✅ Откликнуться", callback_data='start_response')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=user_menu)


def profile_keyboard():
    profile_button = [
        [InlineKeyboardButton(text='Что сейчас в вашей профиле', callback_data='profile_status')],
        [InlineKeyboardButton(text='📝Изменить резюме_id ', callback_data='up_d_user')],
        [InlineKeyboardButton(text='📝Изменить код авторизации', callback_data='up_d_authorization_code')],
        [InlineKeyboardButton(text='📝Изменить сопроводительное письмо', callback_data='up_d_cover_letter')],
        [InlineKeyboardButton(text="📚 Удалить Профиль", callback_data='delete_profile')],
        [InlineKeyboardButton(text="🔙Вернуться на главную", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=profile_button)


def back_to_profile_keyboard():
    back_button = [
        [InlineKeyboardButton(text='🔙Вернуться в профиль', callback_data='back_to_profile')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=back_button)


def menu_delite_profile():
    delite_button = [
        [InlineKeyboardButton(text="❌Удалить профиль❌", callback_data='confirm_profile_deletion')],
        [InlineKeyboardButton(text="🔙Вернуться в меню профиля", callback_data='back_to_profile')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=delite_button)
