from aiogram import Router
from create_bot import bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import DatabaseManager, engine
from database.requests import UserRequests
from keyboards.state import Post
from keyboards.inline_kb import (menu, authorized_user_menu, profile_keyboard,
                                 back_to_profile_keyboard, menu_delite_profile)


class UserHandler:
    def __init__(self):
        self.db_manager = DatabaseManager(engine)
        self.user_requests = UserRequests(self.db_manager)
        self.router = Router()
        self.register_handlers()

    def register_handlers(self):
        self.router.message(CommandStart())(self.cmd_start_inline)
        self.router.message(Command('Post'))(self.state_resume_id)
        self.router.message(Post.resume_id)(self.state_authorization_code)
        self.router.message(Post.authorization_code)(self.state_cover_letter)
        self.router.message(Post.cover_latter)(self.handle_cover_letter)
        self.router.callback_query(lambda c: c.data == 'fill_data')(self.state_resume_id)
        self.router.callback_query(lambda c: c.data == 'information')(self.process_information)
        self.router.callback_query(lambda c: c.data == 'profile_keyboard')(self.profile_menu)
        self.router.callback_query(lambda c: c.data == 'back_to_main')(self.back_to_main)
        self.router.callback_query(lambda c: c.data == 'back_to_profile')(self.back_to_profile)
        self.router.callback_query(lambda c: c.data == 'profile_status')(self.request_profile_status)
        self.router.callback_query(lambda c: c.data == 'delete_profile')(self.delete_profile)
        self.router.callback_query(lambda c: c.data == 'up_d_user')(self.update_user)
        self.router.callback_query(lambda c: c.data == 'up_d_authorization_code')(self.update_authorization_code)
        self.router.callback_query(lambda c: c.data == 'up_d_cover_letter')(self.update_cover_letter)
        self.router.callback_query(lambda c: c.data == 'confirm_profile_deletion')(self.delite_profile_button)
        self.router.message()(self.handle_text_input)

    async def cmd_start_inline(self, message: Message):
        user_id = message.from_user.id

        try:
            # Проверяем, существует ли пользователь в базе данных
            user_exists = await self.user_requests.user_exists(user_id)

            if user_exists:
                await message.answer("Добро пожаловать обратно!", reply_markup=authorized_user_menu())
            else:
                await message.answer("Добро пожаловать!", reply_markup=menu())

        except Exception as e:
            await message.answer("Произошла ошибка при проверке пользователя. Пожалуйста, попробуйте еще раз.")
            print(f"Ошибка: {e}")

    async def state_resume_id(self, callback_query: CallbackQuery, state: FSMContext):
        await bot.answer_callback_query(callback_query.id)
        user_id = callback_query.from_user.id

        try:
            user_exists = await self.user_requests.user_exists(user_id)

            if user_exists:
                await bot.send_message(user_id,
                                       "Пользователь с таким ID уже существует."
                                       "Вы можете изменить данные или удалить профиль.")
                return """прерываем выполнение, если пользователь уже существует"""

            """С данного места начинает FSM."""
            await state.update_data(user_id=user_id)
            await state.set_state(Post.resume_id)
            await bot.send_message(user_id, f"Ваш ID сохранён: {user_id}. Пожалуйста, введите resume_id.")

        except Exception as e:
            await bot.send_message(user_id,
                                   "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.")
            print(f"Ошибка: {e}")

    async def state_authorization_code(self, message: Message, state: FSMContext):
        try:
            await state.update_data(resume_id=message.text)
            await state.set_state(Post.authorization_code)
            await message.answer("Ваш resume_id сохранён! Пожалуйста, введите authorization_code.")
        except Exception as e:
            await message.answer("Произошла ошибка при сохранении resume_id. Пожалуйста, попробуйте еще раз.")
            print(f"Ошибка: {e}")

    async def state_cover_letter(self, message: Message, state: FSMContext):
        try:
            await state.update_data(authorization_code=message.text)
            await state.set_state(Post.cover_latter)
            await message.answer("Ваш authorization_code сохранён! Пожалуйста, введите ваше сопроводительное письмо.")
        except Exception as e:
            await message.answer("Произошла ошибка при сохранении authorization_code. Пожалуйста, попробуйте еще раз.")
            print(f"Ошибка: {e}")

    async def handle_cover_letter(self, message: Message, state: FSMContext):
        cover_letter = message.text

        try:
            await state.update_data(cover_letter=cover_letter)

            data = await state.get_data()

            user_data = {
                'user_id': data['user_id'],
                'resume_id': data['resume_id'],
                'authorization_code': data['authorization_code'],
                'cover_letter': cover_letter
            }

            added = await self.user_requests.add_user(user_data)

            if not added:
                await message.answer("Не удалось сохранить данные. Убедитесь, что пользователь существует.")
            else:
                await message.answer(
                    f"Полученные данные сохранены: \n\n"
                    f"Telegram_ID: {data['user_id']}\n"
                    f"Резюме ID: {data['resume_id']}\n"
                    f"Код авторизации: {data['authorization_code']}\n"
                    f"Сопроводительное письмо: {data['cover_letter']}",
                    reply_markup=authorized_user_menu()
                )

        except Exception as e:
            await message.answer("Произошла ошибка при сохранении данных. Пожалуйста, попробуйте еще раз.")
            """Логировать ошибку для отладки"""
            print(f"Ошибка: {e}")

        finally:
            await state.clear()

        """
        В данном месте FSM отработал
        """

    async def process_information(self, callback_query: CallbackQuery):
        info_text = (
            "А КУДА ТУТ ЖМАТЬ СОБСТВЕННО?\n\n"
            "Не пугайтесь! Ничего сложного сейчас все объясню!\n\n"
            "Если вы зашли первый раз, то основная задача - это заполнить данные для отклика.\n\n"
            "1. Нажмите на кнопку 'Авторизация через HH' для входа.\n"
            "2. Заполните необходимые данные для отклика.\n"
            "3. Если у вас есть вопросы, не стесняйтесь обращаться за помощью."
        )
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, info_text)

    async def profile_menu(self, callback_query: CallbackQuery):
        await callback_query.answer(text="Вы выбрали меню профиля!")
        await callback_query.message.edit_text("Меню профиля!", reply_markup=profile_keyboard())

    async def back_to_main(self, callback_query: CallbackQuery):
        await callback_query.answer(text="Вы вернулись в главное меню")
        await callback_query.message.edit_text("Главное меню", reply_markup=authorized_user_menu())

    async def back_to_profile(self, callback_query: CallbackQuery):
        await self.profile_menu(callback_query)

    async def delete_profile(self, callback_query: CallbackQuery):
        await callback_query.message.edit_text('Вы выбрали меню удаления профиля', reply_markup=menu_delite_profile())

    async def request_profile_status(self, callback_query: CallbackQuery):
        await callback_query.answer(text="Заполненные данные вашего профиля", show_alert=True)

        user_id = callback_query.from_user.id  # Получаем user_id из callback_query

        try:
            # Запрашиваем данные пользователя из базы данных
            user_data = await self.user_requests.get_user_data(user_id)

            if user_data:
                # Формируем сообщение с данными пользователя
                profile_info = (
                    f"User ID: {user_data['user_id']}\n"
                    f"Resume ID: {user_data['resume_id']}\n"
                    f"Authorization Code: {user_data['authorization_code']}\n"
                    f"Cover Letter: {user_data['cover_letter']}"
                )
                await callback_query.message.edit_text(profile_info, reply_markup=back_to_profile_keyboard())
            else:
                await callback_query.message.edit_text("Профиль не найден. Убедитесь, что вы зарегистрированы.",
                                                       reply_markup=back_to_profile_keyboard())

        except Exception as e:
            await callback_query.message.edit_text(
                "Произошла ошибка при получении данных профиля. Пожалуйста, попробуйте еще раз.")
            print(f"Ошибка: {e}")

    async def update_user(self, callback_query: CallbackQuery):
        await callback_query.answer(text="Введите новый resume_id для обновления.", show_alert=True)
        await callback_query.message.edit_text("Введите новый resume_id для обновления.")

        user_id = callback_query.from_user.id
        self.user_requests.current_user_id = user_id
        self.user_requests.current_update_type = 'resume_id'

    async def update_authorization_code(self, callback_query: CallbackQuery):
        await callback_query.answer(text="Введите новый authorization_code для обновления.", show_alert=True)
        await callback_query.message.edit_text("Введите новый authorization_code для обновления.")

        user_id = callback_query.from_user.id
        self.user_requests.current_user_id = user_id
        self.user_requests.current_update_type = 'authorization_code'

    async def update_cover_letter(self, callback_query: CallbackQuery):
        await callback_query.answer(text="Введите новое сопроводительное письмо для обновления.")
        await callback_query.message.edit_text("Введите новое сопроводительное письмо для обновления.")

        user_id = callback_query.from_user.id
        self.user_requests.current_user_id = user_id
        self.user_requests.current_update_type = 'cover_letter'

    async def handle_text_input(self, message: Message):
        user_id = message.from_user.id
        update_type = self.user_requests.current_update_type

        try:
            if update_type == 'resume_id':
                await self.user_requests.update_user(user_id, {'resume_id': message.text})
                await message.answer("Resume ID успешно обновлён!")

            elif update_type == 'authorization_code':
                await self.user_requests.update_user(user_id, {'authorization_code': message.text})
                await message.answer("Authorization Code успешно обновлён!")

            elif update_type == 'cover_letter':
                await self.user_requests.update_user(user_id, {'cover_letter': message.text})
                await message.answer("Сопроводительное письмо успешно обновлено!")

            """Если обновление прошло успешно, возвращаем в меню профиля"""
            await message.answer("Вы вернулись в меню профиля!", reply_markup=profile_keyboard())

        except Exception as e:
            """Обработка ошибок"""
            await message.answer("Не удалось обновить данные. Убедитесь, что пользователь существует.")

        finally:
            """Сбросим текущий тип обновления после обработки"""
            self.user_requests.current_update_type = None

    async def delite_profile_button(self, callback_query: CallbackQuery):
        await callback_query.answer(text="Вы подтвердили удаление профиля", show_alert=True)
        user_id = callback_query.from_user.id

        try:
            await self.user_requests.delete_user(user_id)
            await callback_query.message.edit_text("Профиль успешно удалён.")
        except Exception as e:
            await callback_query.message.edit_text("Не удалось удалить профиль. Убедитесь, что профиль существует.")
