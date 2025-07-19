# TODO List (Altenar internship project)

## Полный запуск через Docker Compose
Создаем в корне .env и указываем параметры
```
DATABASE_URL=postgresql://user:password@localhost:5432/tododb # URL подключение к БД для бекенда
POSTGRES_DB=tododb # Имя БД
POSTGRES_USER=user # Пользователь БД
POSTGRES_PASSWORD=password # Пароль БД
REACT_APP_API_BASE_URL=http://localhost:8000 # url подключения к бекенду
```

```
docker compose up -d
```

## Локальный запуск приложения с использованием Docker для базы данных

### Требования
- Docker + Docker Compose
- Python 3.9+
- Node.js 18+

### Установка 

Клонируем проект
```
git clone https://github.com/matveyxsid/todolist
cd todolist
```


### Конфигурация Docker compose
Создаем .env и указываем переменные окружения

```
DATABASE_URL=postgresql://user:password@localhost:5432/tododb # URL подключение к БД для бекенда
POSTGRES_DB=tododb # Имя БД
POSTGRES_USER=user # Пользователь БД
POSTGRES_PASSWORD=password # Пароль БД
REACT_APP_API_BASE_URL=http://localhost:8000 # url подключения к бекенду
```


### Запуск базы данных (PostgresSQL в Docker)
```
docker compose up -d postgres
```


### Backend (Python + FastAPI)

Переходим в директорию backend 

Создаем вируальное окружение
```python -m venv venv```

Активируем окружение
```source venv/bin/activate```

Устанавливаем зависимости
```pip install -r requirements.txt```

Запускаем FastAPI
```uvicorn main:app --reload```

- API: [http://localhost:8000](http://localhost:8000)  
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)


### Frontend (React + TypeScript)
Переходим в директорию frontend

Устанавливает зависимости
```npm install```

В директории frontend/ создаем .env с переменной REACT_APP_API_BASE_URL - задаем адрес API
```
REACT_APP_API_BASE_URL=http://localhost:8000 
```

Запускаем фронтенд
```npm start```

- Фрнтенд: [http://localhost:3000](http://localhost:3000)