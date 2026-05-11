FROM python:3.11.2

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /root/workspace
COPY containers/requirements.txt /root/workspace/requirements.txt

WORKDIR /root/workspace

RUN pip install --upgrade pip setuptools \
    && pip install -r requirements.txt

COPY src/tootooroo /root/workspace/src/tootooroo

RUN chmod +x /root/workspace/src/tootooroo/sqldiff \
    && chmod +x /root/workspace/src/tootooroo/sqlite3 \
    && chmod +x /root/workspace/src/tootooroo/sqlite3_analyzer

WORKDIR /root/workspace/src/tootooroo

EXPOSE 8000

CMD sh -c "python manage.py collectstatic --noinput && \
           gunicorn tootooroo.wsgi:application --bind 0.0.0.0:8000 --workers 3"
