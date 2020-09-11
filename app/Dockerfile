FROM python:3.7
EXPOSE 5000

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY app.py /app
COPY templates /app/templates
COPY worker.py /app
COPY word_count.db /app
COPY models.py /app
COPY task.py /app
COPY test.py /app
CMD redis-server
CMD python app.py
