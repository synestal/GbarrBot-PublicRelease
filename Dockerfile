# ---
# Первый этап: сборка
FROM python:3.9-alpine3.13 as build

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev
COPY requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && mkdir /wheels \
    && pip wheel --no-cache-dir -r /app/requirements.txt -w /wheels


# ---
# Второй этап: минимальный финальный образ
FROM python:3.9-alpine3.13

# Копируем зависимости из первого этапа
COPY --from=build /wheels /wheels
COPY --from=build /app/requirements.txt /app/
RUN pip install --no-cache /wheels/*

COPY main.py config.py blocks.xlsx /app/
WORKDIR /app
ENTRYPOINT ["python3", "main.py"]

