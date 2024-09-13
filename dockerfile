FROM python:3.9.7
WORKDIR /QunatTraing_System
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


ENV PYTHONPATH=/QunatTraing_System:$PYTHONPATH

EXPOSE 5000
ENV FLASK_APP=quant.main.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

COPY  . /QunatTraing_System


CMD ["flask", "run", "--host", "0.0.0.0"]
