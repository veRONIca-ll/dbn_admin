# DUBNA ADMINISTRATION BOT
-- mostly done --
### Имя: 
    телеграм-бот Администрации города Дубна

### Цель:
    оптимизировать обработку запросов пользователся информационно-технического обеспечения Администрации города Дубны

### Задачи:
    1) получать запросы от пользователей 
    2) обрабатывать полученные запросы
    3) предлагать варианты решения по прошлым запросам
    4) записывать в БД новые запросы 
    5) отправлять нерешенный запрос сотрудникам нформационно-технического обеспечения
    6) отслеживать статус актуального запроса 
    7) записывать вариант решения запроса

### Разворачивание проекта: 
    1) Требования
        Python: ^3.6
        elasticsearch: ^8
        postgreSQL
    2) Необходимые библиотеки для работы устновить можно через команду
        pip install requirements.txt
    3) Настроить переменные окружения в файле .env в соответствии с файлом .env.example
    4) Создание таблиц осуществляется в корне проекта по команде
        python /db/start.py
    5) Начальная загрузка схемы таблиц в ES
        bootstrap --config /schema.json
    6) Для синзронизации БД и ES в фоновом режиме
        pgsync --config schema.json --daemon

### Структура проекта:
    main.py - скрипт бота
    data/   - папка файлов с данными, которые нужны для заполения БД (названия файлов, указываются в .env)
        структура файла с категориями: 
            <категория1>\n<категория2>\n...
        структура файла с запросами:
            <описание запроса>;<решение запроса>;<id катеогрии>\n
            ...
    db/ - папка для работы с БД 
        base_insert/     - папка со скриптами для первичного заполнения таблиц
        install/         - папка со скриптом для создания таблиц БД
        start.py         - скрипт для создания таблиц и их заполнения
        db_operations.py - скрипт по работе с БД
    integrations/ - папка со скриптами для работы со сторонними сервисами
       es_integration.py     - скрипт по работе с ES
       trello_integration.py - скрипт по работе с Trello
    job/ 
        sync.py - скрипт по синхронизации задач между Trello и БД
    logs/ - папка для логов
        app.log - логи
    utils/
        helpers.py - вспомогательные функции
        logger.py  - функции для логирования
    .env.example - пример структуры для .env
    scheme.json - схема таблиц для ES



