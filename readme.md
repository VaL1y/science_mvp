# Science Trend Analyzer MVP

Прототип системы анализа научных направлений.

## Возможности MVP

- POST /analyze — анализ одного направления
- POST /compare — сравнение двух направлений
- Пока возвращаются моковые данные

## Запуск

1. Создать виртуальное окружение:

python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

2. Установить зависимости:

pip install -r requirements.txt

3. Создать .env файл

4. Запуск:

uvicorn main:app --reload

Документация:
http://localhost:8000/docs
