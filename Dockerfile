FROM python:latest

WORKDIR /opt/app

COPY . /opt/app/
RUN pip install -r requirements.txt

CMD ["fastapi", "dev", "src/api/main.py", "--host", "0.0.0.0",  "--port", "8001"]
