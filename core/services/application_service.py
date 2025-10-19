from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.methods import SendMessage
from aiogram.types import Message


class ApplicationService:
    states_history_key = 'states_history'
    answers_history_key = 'answers_history'

    @staticmethod
    async def next(state: FSMContext, next_state: State, answer: SendMessage = None, field_state: State = None):  # Метод для назначения следующего узла
        data = await state.get_data()

        states_history = data.get(ApplicationService.states_history_key, [])  # Получает историю состояний или создаем пустую, если нет
        answers_history = data.get(ApplicationService.answers_history_key, [])  # Получает историю ответов или создаем пустую, если нет

        current_state = await state.get_state()  # Берет текущее состояние

        current_state_field = (
            field_state.state.split(":")[-1]
            if field_state else
            (current_state.split(":")[-1] if current_state else None)  # Берет название состояния
        )

        states_history.append({'state': current_state,
                               'field_state': current_state_field})  # Добавляет текущее состояние в список и состояние которое обновляется
        answers_history.append(answer)  # Добавляет answer в список answers

        await state.update_data({ApplicationService.states_history_key: states_history})  # Сохранение
        await state.update_data({ApplicationService.answers_history_key: answers_history})

        await state.set_state(next_state)

        if answer:
            await answer

    @staticmethod
    async def back(state: FSMContext):  # Метод для шага назад
        data = await state.get_data()

        states_history = data.get(ApplicationService.states_history_key)  # Получает историю состояний
        answers_history = data.get(ApplicationService.answers_history_key)  # Получает историю answers

        last_state = states_history.pop()  # Забирает последнее состояние

        data.pop(last_state['field_state'], None)  # Стирает данные последнего поля
        await state.set_data(data)

        if len(answers_history) < 2:
            ValueError('Некуда возвращаться')

        del answers_history[-1]  # Удаляет последний ответ из истории
        await answers_history[-1]  # Ожидает предыдущий ответ

        await state.set_state(last_state['state'])  # Предыдущее состояние

    @staticmethod
    async def skip(state: FSMContext, next_state: State, answer: SendMessage = None, field_state: State = None):  # Метод для пропуска
        await ApplicationService.next(state, next_state, answer, field_state)

    @staticmethod
    async def back_home(state: FSMContext, message: Message):  # Метод для возврата к началу
        await state.clear()
        await start_command_handler(message)  # Вернуться к начальному обработчику
