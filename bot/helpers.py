
def send_list(data) -> str:
    out = ''
    for key in data.keys():
        out += f'{key}. {data[key]}\n'

    return out
