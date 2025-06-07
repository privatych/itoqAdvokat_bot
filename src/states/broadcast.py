from aiogram.fsm.state import State, StatesGroup

class BroadcastState(StatesGroup):
    broadcast_message = State()
    confirm_message = State() 