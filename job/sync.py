import os
import sys
sys.path.append(os.getenv('PATH_TO_APP_FOLDER'))

from db.db_operations import get_unsolved_tasks
from integrations.trello_integration import check_if_done

def sync(context):
    ''' Cинхронизация c Trello и переиндексация ElasticSearch '''
    tasks = get_unsolved_tasks()

    if len(tasks) == 0:
        return
    
    for task in tasks:
        check_if_done(task[0])
    os.system(f"pgsync --config {os.getenv('PATH_TO_APP_FOLDER')}/schema.json")
