FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt --no-cache-dir
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]