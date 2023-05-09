FROM python:3.9

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

RUN mkdir -p /app/backend
COPY . /app/backend

EXPOSE 8080

RUN useradd -m myuser
USER myuser

CMD ["uvicorn", "--app-dir", "./backend" ,"api:app", "--host", "0.0.0.0", "--port", "8080"]
