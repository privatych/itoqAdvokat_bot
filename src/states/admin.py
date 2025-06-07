from aiogram.fsm.state import State, StatesGroup

class AdminState(StatesGroup):
    """Состояния для админ-панели"""
    broadcast_message = State()  # Состояние ожидания сообщения для рассылки
    confirm_message = State()    # Состояние подтверждения рассылки
    waiting_action = State()     # Состояние ожидания действия админа 