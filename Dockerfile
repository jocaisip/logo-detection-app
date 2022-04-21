FROM python:3.8-slim
ADD . /logoapp
WORKDIR /logoapp
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["main.py"]