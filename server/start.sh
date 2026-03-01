#!/bin/bash

# Имя директории для виртуального окружения
VENV_DIR="venv"

# Проверяем, существует ли директория venv
if [ ! -d "$VENV_DIR" ]; then
  echo "Создание виртуального окружения..."
  # Создаем виртуальное окружение
  python -m venv $VENV_DIR
  if [ $? -ne 0 ]; then
    echo "Не удалось создать виртуальное окружение. Убедитесь, что пакет 'python-venv' установлен."
    exit 1
  fi
fi

# Пути к исполняемым файлам внутри venv
PIP_EXEC="$VENV_DIR/bin/pip"
GUNICORN_EXEC="$VENV_DIR/bin/gunicorn"

# Проверяем, существует ли файл requirements.txt (создаем только один раз)
if [ ! -f "requirements.txt" ]; then
  echo "Создание файла requirements.txt..."
  echo "Flask" > requirements.txt
  echo "Flask-SQLAlchemy" >> requirements.txt
  echo "gunicorn" >> requirements.txt
fi

# Устанавливаем зависимости в виртуальное окружение
echo "Установка зависимостей..."
$PIP_EXEC install -r requirements.txt

# Запускаем сервер с помощью gunicorn из виртуального окружения
echo "Запуск сервера..."
$GUNICORN_EXEC --bind 0.0.0.0:5000 server:app
