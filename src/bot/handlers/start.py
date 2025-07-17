from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    """
    Handler for the /start command.
    """
    await message.answer("🤖 NEXUS Gear на связи!")