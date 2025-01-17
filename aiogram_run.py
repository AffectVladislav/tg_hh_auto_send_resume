import asyncio
from create_bot import bot, dp

from handlers.handlers import UserHandler
from keyboards.commands import set_commands
from database.models import async_main


async def main():
    await async_main()
    user_handler = UserHandler()
    dp.include_router(user_handler.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
