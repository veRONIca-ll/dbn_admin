import os
import sys
from elasticsearch import Elasticsearch

sys.path.append(os.getenv('PATH_TO_APP_FOLDER'))

NEEDED_FIELDS = ['description', 'steps']

def _connect_elasticsearch(host, port) -> Elasticsearch:
    ''' Подключение к elasticsearch '''
    _es = None
    _es = Elasticsearch(f"http://{host}:{port}")
    if _es.ping():
        # TODO : log success
        print('Yay Connect')
    else:
        # TODO : log error
        print('Awww it could not connect!')
    return _es

def _create_query(id, msg) -> dict:
    ''' Создание запроса для elasticsearch '''
    words = msg.replace(',', '').split()
    return {"bool" : {
          "must": [
              {"term": {"category_id": id}},
              {"term": {"status": True}}
            ],
        "filter": {
          "terms" : { "description": words }
        }
      }}

def _process_result(response_hits) -> list:
    ''' Обработка полученного результата '''
    tasks = []
    for num, doc in enumerate(response_hits):
        task = {}
        for field in NEEDED_FIELDS:
            task[field] = str(doc['_source'][field]).encode('utf-8').decode('utf-8')
        tasks.append(task)
    return tasks

def search_es(category_id, msg) -> list:
    ''' Поиск уже решенных заявок в elasticsearch по описанию проблемы '''
    _es = _connect_elasticsearch(os.getenv('E_HOST'), os.getenv('E_PORT'))
    response = []
    if _es is not None:
        res = _es.search(index=os.getenv('E_INDEX'), query=_create_query(category_id, msg))
        print(res)
        if res['hits']['total']['value'] != 0:
            response = _process_result(res['hits']['hits'])
    
    return response
