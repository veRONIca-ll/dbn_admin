import os
import sys
sys.path.append(os.getenv('PATH_TO_APP_FOLDER'))

from trello import TrelloClient
from db.db_operations import find_user, get_department_name, add_task, get_unsolved_tasks, update_task

def _connect_trello():
    ''' Подключение к Trello '''
    try:
        trello = TrelloClient(
            api_key=os.getenv('TRELLO_API_KEY'),
            api_secret = os.getenv('TRELLO_API_SECRET')
        )
        return trello
    except Exception:
        print('sad')
        return None

def _card_title(info: list) -> str:
    ''' Создание тайтла для карточки Trello'''
    card_name = ''
    if info[2] is None: # not added fio
        card_name += info[1] + '\n'
    else:
        card_name += info[3] + ' ' + info[2] + ' ' + info[4] + '\n'
    if info[5] is not None:
        card_name += get_department_name(info[5])[0] + '\n'
    return card_name


def create_card(user_id, category_id, msg) -> str:
    ''' Создание новой карточки-заявки '''
    trello = _connect_trello()
    if trello is not None:
        name = _card_title(find_user(user_id)) + '\n--Заявка--\n' + msg
        board = trello.get_board(_find_board_id(trello.list_boards()))
        todo_list =  board.get_list(os.getenv('TODO_LIST_ID'))
        new_card = todo_list.add_card(name)
        if new_card is not None:
            task = add_task(user_id, category_id, new_card.id, msg)
            if task:
                return new_card.short_url
    
    return ''


def check_if_done(card_id: str):
    ''' Проверка завершенности карточек по ID заявки '''
    trello = _connect_trello()
    if trello is not None:
        try:
            card = trello.get_card(card_id)
            print(card.name)
            if card is not None and card.list_id == os.getenv('DONE_LIST_ID') and card.description is not None:
                return update_task(card_id, card.description)
        except Exception:
            print('no such card')
            return ''
