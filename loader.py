from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()

dp = Dispatcher(storage=storage)
