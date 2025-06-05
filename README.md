# Связующий сервер Spotify & DeepSeek Server

Связующий сервер, который:
- Получает сохранённые треки пользователя с локального Spotify API (`127.0.0.1:5001`)
- Отправляет их в DeepSeek-сервис для генерации похожих рекомендаций (`127.0.0.1:5000`)
- Создаёт плейлист или добавляет треки в указанный
- Сохраняет историю операций в SQLite

---

## Установка

### 1. Клонируй проект и перейди в папку
```bash
git clone https://github.com/ipozidaev61/spotify-deekseek-base-api.git
cd spotify-deekseek-base-api
```

### 2. Установи зависимости
```bash
pip install -r requirements.txt
```

### 3. Создай `.env` файл
```ini
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
REFRESH_TOKEN=your_spotify_refresh_token
```

---

## Запуск

```bash
python app.py
```

Сервер запустится по адресу: `http://127.0.0.1:8000`

---

## Эндпоинты

### `POST /v1/playlist`
Создаёт новый плейлист в Spotify на основе сохранённых треков + рекомендаций от DeepSeek.

**Пример:**
```bash
curl -X POST http://127.0.0.1:8000/v1/playlist
```

---

### `POST /v1/playlist/<playlist_id>`
Добавляет рекомендованные треки в указанный плейлист.

**Пример:**
```bash
curl -X POST http://127.0.0.1:8000/v1/playlist/37i9dQZF1DX4JAvHpjipBk
```

---

### `GET /v1/history`
Возвращает историю всех ранее добавленных треков с временем создания.

**Пример ответа:**
```json
[
  {
    "timestamp": "2025-06-05T13:48:29.013Z",
    "tracks": [
      "Daft Punk - One More Time",
      "SZA - Kill Bill"
    ]
  }
]
```

---

## Структура базы данных

Файл: `history.db`  
Таблица: `history`

| Поле      | Тип     | Описание                          |
|-----------|----------|-----------------------------------|
| id        | INTEGER  | Primary key (auto-increment)      |
| timestamp | TEXT     | Время добавления треков           |
| tracks    | TEXT     | Список треков (через `\n`)        |

---

## Требования

- Python 3.8+
- Flask
- requests
- python-dotenv

---

