ARG JINA_VERSION=3.25-py39-standard
FROM jinaai/jina:${JINA_VERSION}
EXPOSE 8080
WORKDIR /app
COPY . ./
RUN pip install -r requirements.txt
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
