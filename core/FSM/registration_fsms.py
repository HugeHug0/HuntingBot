from aiogram.fsm.state import StatesGroup, State


class HunterRegistrationFSM(StatesGroup):
    full_name = State()
    phone_number = State()
    email = State()
    region = State()
    hunting_type = State()
    comment = State()
    confirm = State()

class HuntingBaseRegistrationFSM(StatesGroup):
    name = State()
    region = State()
    services = State()
    contact_person = State()
    contact = State()
    website = State()
    confirm = State()
