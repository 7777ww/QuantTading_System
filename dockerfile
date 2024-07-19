FROM python:3.9.7
WORKDIR /quant
COPY  . /quant
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# CMD  ["python", "main.py"]
CMD ["tail", "-f", "/dev/null"]
