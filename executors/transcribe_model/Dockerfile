ARG JINA_VERSION=3.25-py39-standard

FROM jinaai/jina:${JINA_VERSION}

# install ffmpeg
RUN apt update && apt -y install ffmpeg

# install requirements before copying the workspace
COPY requirements.txt /requirements.txt
RUN pip install --default-timeout=1000 --compile -r requirements.txt

# setup the workspace
COPY . /workdir/
WORKDIR /workdir

ENTRYPOINT ["jina", "executor", "--uses", "config.yml"]