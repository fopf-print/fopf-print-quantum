FROM python:3.12

COPY . /app
WORKDIR /app

ENV FOPF_PRINT_ENVIRONMENT=prod
ENV PATH=/root/.local/bin:$PATH

RUN \
    curl -sSL https://install.python-poetry.org | python3 - && \
    poetry install

CMD [ "poetry", "run", "quantum", "run-bot" ]
