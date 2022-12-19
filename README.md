## Chat WebServer

Python >= 3.9

для разработки необходимо:
Установить глобально `pre-commit`

    $ python3 -m pip install --user pre-commit

Перейти в папку с проектом
Инициализацию виртуального окружения

    $ python3 -m venv .venv

Активировать виртуальное окружение

    $ source .venv/bin/activate

Инициализировать `pre-commit`

    $ pre-commit init

Запуск тестов и вывод результатов в консоль:

    $ py.test --cov .

Запуск тестов с отчетом (для отображения в IDE):

    $ py.test --cov-report xml:cov.xml --cov .

Запуск тестов с отчетом для SonarQube:

    $ python3 -m pytest -o junit_family=xunit1 --cov-report xml:coverage-reports/coverage.xml --cov=. --junitxml=coverage-reports/result.xml .

Для запуска проверок без коммита нужно выполнить команду:

    $ pre-commit run --all-files

<details>
<summary>Проектное задание третьего спринта</summary>
# Проектное задание третьего спринта

Спроектируйте и реализуйте мессенджер для получения и обработки сообщений от клиента.

Кроме основного задания, выберите из списка дополнительные требования.
У каждого требования есть определённая сложность, от которой зависит количество баллов.
Необходимо выбрать такое количество заданий, чтобы общая сумма баллов была больше или равна `4`.
Выбор заданий никак не ограничен: можно выбрать все простые или одно среднее и два простых, или одно продвинутое, или решить все.

## Описание задания

### `Сервер`

Реализовать сервис, который обрабатывает поступающие запросы от клиентов;

Условия и требования:

1. Подключенный клиент добавляется в "общий" чат, где находятся ранее подключенные клиенты;
2. После подключения новому клиенту доступные последние N (по умолчанию 20) сообщений из общего чата;
3. Повторно подключенный клиент имеет возможность просмотреть все ранее непрочитанные сообщения до момента последнего опроса (как из общего чата, так и приватные);
4. По умолчанию сервер стартует на локальном хосте (127.0.0.1) и на 8000 порту (иметь возможность задавать любой);
5. Можно не проектировать БД: информацию хранить в памяти и/или десериализовать/сериализировать в файл (формат на выбор) и восстанавливать при старте сервера;

<details>
<summary> Список возможных методов для взаимодействия (можно изменять) </summary>

1. Подключиться к общему чату

```python
POST /connect
```

2. Получить статус и информацию о чатах

```python
GET /status
```

3. Отправить сообщение в общий чат или определенному пользователю в приватный чат

```python
POST /send
```

</details>

### `Клиент`

Реализовать приложение, который умеет подключаться к серверу и обмениваться сообщениями;

Условия и требования:

1. После подключения клиент может отправлять сообщения в "общий" чат;
2. Возможность отправки сообщения в приватном чате (1-to-1) любому участнику из общего чата;
3. Разрабатывать UI не надо: можно выводить информацию в консоль или использовать лог-файлы;

### Дополнительные требования (отметить [Х] выбранные пункты):

- [x] (1 балл) Период жизни доставленных сообщений — 1 час (по умолчанию).
- [x] (1 балл) Клиент может отправлять не более 20 (по умолчанию) сообщений в общий чат в течение определенного периода - 1 час (по умолчанию). В конце каждого периода лимит обнуляется;
- [x] (1 балл) Возможность комментировать сообщения;
- [-] (2 балла) Возможность создавать сообщения с заранее указанным временем отправки; созданные, но неотправленные сообщения можно отменить;
- [x] (2 балла) Возможность пожаловаться на пользователя. При достижении лимита в 3 предупреждения, пользователь становится "забанен" - невозможность отправки сообщений в течение 4 часов (по умолчанию);
- [ ] (3 балла) Возможность отправлять файлы различного формата (объёмом не более 5Мб, по умолчанию).
- [ ] (3 балла) Пользователь может подключиться с двух и более клиентов одновременно. Состояния должны синхронизироваться между клиентами.
- [-] (3 балла) Возможность создавать кастомные приватные чаты и приглашать в него других пользователей. Неприглашенный пользователь может "войти" в такой чат только по сгенерированной ссылке и после подтверждения владельцем чата.
- [x] \*\*(5 баллов) Реализовать кастомную реализацию для взаимодействия по протоколу `http` (можно использовать `asyncio.streams`);

## Требования к решению

1. Описать документацию по разработанному API: вызов по команде/флагу для консольного приложения или эндпойнт для http-сервиса.
2. Используйте концепции ООП.
3. Используйте аннотацию типов.
4. Предусмотрите обработку исключительных ситуаций.
5. Приведите стиль кода в соответствие pep8, flake8, mypy.
6. Логируйте результаты действий.
7. Покройте написанный код тестами.

## Рекомендации к решению

1. Можно использовать внешние библиотеки, но не фреймворки (описать в **requirements.txt**).
