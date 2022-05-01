import re

def send_list(data) -> str:
    out = ''
    for key in data.keys():
        out += f'{key}. {data[key]}\n'

    return out

def split_into_fullname(id: int, message: str, is_admin: bool) -> dict:
    data = message.split()
    return {
        'user_id': id,
        'first_name': data[1],
        'second_name': data[0],
        'middle_name': data[2],
        'admin': is_admin,
    }

def pretty_output(response) -> str:
    text = ''
    for res in response:
        text += f"<b>{res['description']}</b>\n{res['steps']}\n"

    return text
