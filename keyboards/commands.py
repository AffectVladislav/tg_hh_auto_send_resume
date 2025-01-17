from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot):
    commands = [
        BotCommand(command='start', description='Команда авторизации в приложении.')
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
