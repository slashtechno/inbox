FROM python:3.12

RUN pip install poetry


RUN mkdir /app
WORKDIR /app

COPY . /app

RUN ["poetry", "install"]

ENTRYPOINT ["poetry", "run", "--", "python", "-m", "uvicorn", "inbox.main:app", "--host", "0.0.0.0", "--port", "8000"]