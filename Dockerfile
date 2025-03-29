FROM python:3.12-alpine

RUN apk update
RUN apk add tesseract-ocr tesseract-ocr-data-deu ghostscript pngquant jbig2enc jbig2dec

WORKDIR /app

RUN pip install 'poetry==2.0.1'
RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml ./

RUN poetry install --only main --no-interaction --no-ansi

COPY ./src .

USER 1000:100

ENTRYPOINT ["python", "main.py"]