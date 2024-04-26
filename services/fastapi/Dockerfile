FROM python:3.10-slim

RUN apt update && apt -y install ffmpeg
EXPOSE 8000
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code/
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]