-- Создание базы данных
CREATE DATABASE english_card_db;

-- Подключаемся к english_card_db

-- Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица слов
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    word_en VARCHAR(100) NOT NULL,
    word_ru VARCHAR(100) NOT NULL,
    is_common BOOLEAN DEFAULT TRUE,  -- TRUE = общее слово для всех, FALSE = личное
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица связи пользователей и слов (статистика изучения)
CREATE TABLE user_words (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    word_id INTEGER NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    is_correct BOOLEAN DEFAULT FALSE,  -- выучил ли пользователь слово
    attempts INTEGER DEFAULT 0,         -- количество попыток
    correct_answers INTEGER DEFAULT 0,  -- количество правильных ответов
    last_practiced TIMESTAMP,
    UNIQUE(user_id, word_id)  -- чтобы не дублировать связи
);

-- Индексы для ускорения поиска
CREATE INDEX idx_user_words_user_id ON user_words(user_id);
CREATE INDEX idx_user_words_word_id ON user_words(word_id);
CREATE INDEX idx_words_is_common ON words(is_common);