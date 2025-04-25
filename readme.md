## YaDisk 

This service was created as an entry to the *Yandex Autumn Backend School*. Service works with files and folders object abstractions. Functional requirements and swagger files are in the requirements folder. While programming the service, a lot of experience was gained with async **sqlalchemy** sessions, **fastapi** framework, and **pytest** library. The service contains APIs and docs for new users, as well as written tests for QA.

## Technologies
*Python 3.13, fastapi 0.111, aiosqlite, pytest, sqlalchemy, Docker*


## Disk Items API
*`POST /imports` Imports disk items. Importing existing items updates them.*

**Request Parameters:**
- Request body: `DiskItemsDTO`
  - `items`: List of items to import/update
  - `updateDate`: Update date (guaranteed to increase monotonically)

**Responses:**
- `200 OK`: Successful import
- `400 Bad Request`: Validation error

*`DELETE /delete/{id}` Deletes an item by ID.*

**Parameters:**
- `id`: Item ID (string)
- `date`: Deletion date (`ConvertedTimedate`)

**Responses:**
- `200 OK`: Successful deletion
- `400 Bad Request`: Validation error
- `404 Not Found`: Item not found


*`GET /nodes/{id}` Returns information about an item by ID.*

**Parameters:**
- `id`: Item ID (string)

**Response:**
- `200 OK`: Item information in `DiskItemRetreweSchema` format
- `404 Not Found`: Item not found


*`GET /updates` Returns a list of files updated within the last 24 hours inclusive [date - 24h, date].*

**Query Parameters:**
- `date`: Date and time (`ConvertedTimedate`)

**Response:**
- `200 OK`: List of updated items in `HistoryResponse` format
- `400 Bad Request`: Validation error


*`GET /node/{id}/history` Returns the update history for an item within the specified half-interval [from, to).*

**Query Parameters:**
- `id`: Item ID (string)
- `dateStart`: Start date (`datetime`)
- `dateEnd`: End date (`datetime`)

**Response:**
- `200 OK`: Update history in `HistoryResponse` format
- `400 Bad Request`: Validation error (if dateStart > dateEnd)
- `404 Not Found`: Item not found

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