FROM python:3.7
EXPOSE 5000
ENV PYTHONUNBUFFERED=0
WORKDIR /code
ADD example /code
RUN pip install -r requirements.txt
# for testing package
ADD . /emoji_feedback
RUN pip install -e /emoji_feedback
CMD python server.py