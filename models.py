import atexit
import os

from dotenv import load_dotenv
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship

load_dotenv()

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user_words = relationship("UserWord", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word_en = Column(String(100), nullable=False)
    word_ru = Column(String(100), nullable=False)
    is_common = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    user_words = relationship("UserWord", back_populates="word")

    def __repr__(self):
        return f"<Word(id={self.id}, word_en='{self.word_en}')>"


class UserWord(Base):
    __tablename__ = "user_words"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    is_correct = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    last_practiced = Column(DateTime)

    user = relationship("User", back_populates="user_words")
    word = relationship("Word", back_populates="user_words")

    __table_args__ = (UniqueConstraint("user_id", "word_id"),)

    def __repr__(self):
        return f"<UserWord(user_id={self.user_id}, word_id={self.word_id})>"


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        db_url = (
            f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
            f"{os.getenv('DB_PASSWORD', 'postgres')}@"
            f"{os.getenv('DB_HOST', 'localhost')}:"
            f"{os.getenv('DB_PORT', '5432')}/"
            f"{os.getenv('DB_NAME', 'english_card_db')}"
        )
        _engine = create_engine(db_url)
        atexit.register(_engine.dispose)
    return _engine


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
