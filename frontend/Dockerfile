FROM python:3.9

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

RUN mkdir -p /app/frontend
COPY . /app/frontend/

RUN useradd -m myuser
USER myuser

CMD ["sh", "-c", "streamlit run --server.port $FRONTEND_PORT /app/frontend/streamlit_app.py"]
