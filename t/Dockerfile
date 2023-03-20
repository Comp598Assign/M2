FROM python

COPY /app .

RUN pip freeze > requirements.txt
RUN pip3 install -r requirements.txt
CMD ["python3", "app.py", "15000"]
