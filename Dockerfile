FROM python:3.12-slim

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./src /src/

EXPOSE 80

VOLUME [ "/src/db_data" ]

CMD ["fastapi", "run", "main.py", "--port", "80", "--workers", "4"]