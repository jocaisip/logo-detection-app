FROM python:3.8-slim
ADD . /logoapp
WORKDIR /logoapp
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 git -y
#RUN apt-get update && apt-get install -y python3-opencv
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["main.py"]