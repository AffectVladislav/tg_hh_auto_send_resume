from aiogram.fsm.state import State, StatesGroup


class Post(StatesGroup):
    user_id = State()
    resume_id = State()
    authorization_code = State()
    cover_latter = State()
