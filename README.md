# TODO List (Altenar internship project)

## Полный запуск через Docker Compose

**В процессе**


## Локальный запуск приложения с использованием Docker для базы данных

### Требования
- Docker + Docker Compose
- Python 3.10+
- Node.js 18+

### Установка 

Клонируем проект
```
git clone https://github.com/matveyxsid/todolist
cd todolist
```


### Конфигурация
Создайте .env и укажите переменные окружения

```
DATABASE_URL=postgresql://user:password@localhost:5432/tododb
POSTGRES_DB=tododb
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```


### Запуск базы данных (PostgresSQL в Docker)
```
docker compose up -d postgres
```


### Backend (Python + FastAPI)

Переходим в директорию backend 

Создаем вируальное окружение
```python -m venv venv```

Активируем
```source venv/bin/activate```

Устанавливаем зависимости
```pip install -r requirements.txt```

Запускаем FastAPI
```uvicorn app.main:app --reload```

- API: [http://localhost:8000](http://localhost:8000)  
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)


### Frontend (React + TypeScript)
Переходим в директорию frontend

Устанавливает зависимости
```npm install```

Запускаем фронтенд
```npm start```

- Фрнтенд: [http://localhost:3000](http://localhost:3000)