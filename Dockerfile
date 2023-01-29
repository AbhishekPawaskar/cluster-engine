FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /src
ADD . /src
RUN pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
