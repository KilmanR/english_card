from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, 
    DateTime, ForeignKey, func
)
from sqlalchemy.orm import (
    declarative_base, relationship, sessionmaker
)
import os

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user_words = relationship('UserWord', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Word(Base):
    """Модель слова"""
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    word_en = Column(String(100), nullable=False)
    word_ru = Column(String(100), nullable=False)
    is_common = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    user_words = relationship('UserWord', back_populates='word')

    def __repr__(self):
        return f"<Word(id={self.id}, word_en='{self.word_en}')>"


class UserWord(Base):
    """Модель связи пользователь-слово (статистика)"""
    __tablename__ = 'user_words'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    word_id = Column(Integer, ForeignKey('words.id'), nullable=False)
    is_correct = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    last_practiced = Column(DateTime)

    user = relationship('User', back_populates='user_words')
    word = relationship('Word', back_populates='user_words')

    def __repr__(self):
        return f"<UserWord(user_id={self.user_id}, word_id={self.word_id})>"


def get_engine():
    """Создаёт движок БД"""
    db_url = (
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', 'postgres')}@"
        f"localhost:5432/english_card_db"
    )
    return create_engine(db_url)


def init_db():
    """Инициализация БД (создание таблиц)"""
    engine = get_engine()
    Base.metadata.create_all(engine)