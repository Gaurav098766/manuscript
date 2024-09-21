FROM python:3.10

WORKDIR /fastapi-code

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /fastapi-code/

CMD ["python3", "runserver.py"]