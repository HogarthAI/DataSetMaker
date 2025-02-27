FROM python:latest

WORKDIR /opt/app

COPY ./requirements.txt /opt/app/requirements.txt
RUN pip install -r requirements.txt

COPY . . 

CMD ["fastapi", "dev", "src/api/main.py", "--host", "0.0.0.0",  "--port", "8001"]
