## YaDisk 

This service was created as an entry to the *Yandex Autumn Backend School*. Service works with files and folders object abstractions. Functional requirements and swagger files are in the requirements folder. While programming the service, a lot of experience was gained with async **sqlalchemy** sessions, **fastapi** framework, and **pytest** library. The service contains APIs and docs for new users, as well as written tests for QA.

## Basic Overview
Service inserts and updates self-referential tree structured data. It can also delete and retrieve saved items. All changes to the items should somehow propagate to the parents and change their properties, such as size and last update time. The tricky part is to somehow manage the updates without too much overhead. Also, all except deleted old data should be kept for history.

## Technologies
*Python 3.13, fastapi 0.111, aiosqlite, pytest, sqlalchemy, Docker*

## API
# Disk Items API

API для работы с элементами диска (файлами и папками) с возможностью импорта, удаления, получения информации и истории изменений.

## Общие ответы

- `400 Bad Request` - Неверная схема документа или неверные входные данные
- `404 Not Found` - Элементы не найдены
- `422 Unprocessable Entity` - Возвращает код 400 вместо 422

## Эндпоинты

### Импорт элементов

`POST /imports`

Импортирует элементы диска. Импорт существующих элементов обновляет их.

**Параметры запроса:**
- Тело запроса: `DiskItemsDTO` (опционально)
  - `items`: Список элементов для импорта/обновления
  - `updateDate`: Дата обновления (гарантировано монотонное увеличение)

**Ответы:**
- `200 OK`: Успешный импорт
- `400 Bad Request`: Ошибка валидации

## Удаление элемента

`DELETE /delete/{id}`

Удаляет информацию об элементе по ID.

**Параметры:**
- `id`: ID элемента (строка)
- `date`: Дата удаления (`ConvertedTimedate`)

**Ответы:**
- `200 OK`: Успешное удаление
- `400 Bad Request`: Ошибка валидации
- `404 Not Found`: Элемент не найден

## Получение информации об элементе

`GET /nodes/{id}`

Возвращает информацию об элементе по ID.

**Параметры:**
- `id`: ID элемента (строка)

**Ответ:**
- `200 OK`: Информация об элементе в формате `DiskItemRetreweSchema`
- `404 Not Found`: Элемент не найден

## Получение обновлений

`GET /updates`

Возвращает список файлов, обновленных за последние 24 часа включительно [date - 24h, date].

**Параметры запроса:**
- `date`: Дата и время (`ConvertedTimedate`)

**Ответ:**
- `200 OK`: Список обновленных элементов в формате `HistoryResponse`
- `400 Bad Request`: Ошибка валидации

## Получение истории изменений элемента

`GET /node/{id}/history`

Возвращает историю изменений элемента за заданный полуинтервал [from, to).

**Параметры запроса:**
- `id`: ID элемента (строка)
- `dateStart`: Начальная дата (`datetime`)
- `dateEnd`: Конечная дата (`datetime`)

**Ответ:**
- `200 OK`: История изменений в формате `HistoryResponse`
- `400 Bad Request`: Ошибка валидации (если dateStart > dateEnd)
- `404 Not Found`: Элемент не найден
## Project setup
1. Clone the repository with the command `git clone https://github.com/Lixerus/YandexBackendEntry.git`
2. Run 2 following commands in cmd in the root folder:
    1. `docker build . -t yadisk`
    2. `docker create --name yadisk -p 80:80 --restart=always yadisk`
3. To start and stop newly created container use
    1. `docker start yadisk`
    2. `docker stop yadisk`
4. Interactive docs are on `http//localhost:80/docs`
5. To run tests, start the container and run `pytest` in the root folder.

## Example
Scenario with adding, updating, retreving, history and deletion.
![scenario](YaDisk_basic_scenario.gif)