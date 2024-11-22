## YaDisk 

This service was creted as an entry to the *Yandex Autumn Backend School*. Service works with files and folders object abstractions. Functional requirements and swagger files are in requirements folder. While programming the service a lot of experince was gained with async **sqlalchemy** sessions, **fastapi** framework and **pytest** library. Service contains api and docs for new users as well as written tests for QA.

## Basic Overview
 
Service inserts and updates self-referential tree structured data. It can also delete and retreve saved items. All changes to an items should somehow propagate to the parents and change their properties such as size and lastupdate time. The tricky part is to somehow manage the updates without too much overhead. Also all except deleted old data should be kept for history.

## Technologies 

*Python 3.13, fastapi 0.111, aiosqlite, pytest, sqlalchemy, docker*

# Project setup

1. Clone the repositary with command `git clone https://github.com/Lixerus/YandexBackendEntry.git`
2. Run 2 following commands in cmd in root folder:
    1. `docker build . -t yadisk`
    2. `docker create --name yadisk -p 80:80 --restart=always yadisk`
3. To start and stop newly created container use
    1. `docker start yadisk`
    2. `docker stop yadisk`
4. Interactive docs are on `http//localhost:80/docs`
5. To run tests start the container and run `pytest` in root folder

## Example
Scenario with adding, updating, retreving, history and deletion.
![scenario](YaDisk_basic_scenario.gif)