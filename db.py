from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models import User, Word, UserWord, get_engine
from datetime import datetime


def get_or_create_user(username: str) -> User:
    engine = get_engine()
    with Session(engine) as session:
        user = session.query(User).filter(User.username == username).first()

        if not user:
            try:
                user = User(username=username)
                session.add(user)
                session.commit()
                session.refresh(user)
            except IntegrityError:
                session.rollback()
                user = session.query(User).filter(User.username == username).one()

        return user


def get_common_words() -> list[Word]:
    engine = get_engine()
    with Session(engine) as session:
        return session.query(Word).filter(Word.is_common).all()


def get_user_words(user_id: int) -> list[Word]:
    engine = get_engine()
    with Session(engine) as session:
        words = (
            session.query(Word)
            .join(UserWord, Word.id == UserWord.word_id, isouter=True)
            .filter((Word.is_common) | (UserWord.user_id == user_id))
            .distinct()
            .all()
        )

        return words


def add_word(word_en: str, word_ru: str, user_id: int = None) -> int:
    engine = get_engine()
    with Session(engine) as session:
        is_common = user_id is None

        word = Word(word_en=word_en, word_ru=word_ru, is_common=is_common)
        session.add(word)
        session.flush()

        if user_id:
            user_word = UserWord(user_id=user_id, word_id=word.id)
            session.add(user_word)

        session.commit()
        session.refresh(word)

        return word.id


def delete_word(word_id: int, user_id: int) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        word = session.query(Word).filter(Word.id == word_id).first()

        if word and not word.is_common:
            session.query(UserWord).filter(
                UserWord.user_id == user_id, UserWord.word_id == word_id
            ).delete()

            session.delete(word)
            session.commit()
            return True

        return False


def update_word_stats(user_id: int, word_id: int, is_correct: bool):
    engine = get_engine()
    with Session(engine) as session:
        user_word = (
            session.query(UserWord)
            .filter(UserWord.user_id == user_id, UserWord.word_id == word_id)
            .first()
        )

        if not user_word:
            user_word = UserWord(
                user_id=user_id, word_id=word_id, attempts=0, correct_answers=0
            )
            session.add(user_word)

        user_word.attempts += 1
        if is_correct:
            user_word.correct_answers += 1
        user_word.is_correct = is_correct
        user_word.last_practiced = datetime.now()

        session.commit()


def get_user_stats(user_id: int) -> dict:
    engine = get_engine()
    with Session(engine) as session:
        user_words = session.query(UserWord).filter(UserWord.user_id == user_id).all()

        total_words = len(user_words)
        total_correct = sum(uw.correct_answers for uw in user_words)
        total_attempts = sum(uw.attempts for uw in user_words)
        learned_words = sum(1 for uw in user_words if uw.is_correct)

        return {
            "total_words": total_words,
            "total_correct": total_correct,
            "total_attempts": total_attempts,
            "learned_words": learned_words,
        }


def get_user_personal_words(user_id: int) -> list[Word]:
    engine = get_engine()
    with Session(engine) as session:
        words = (
            session.query(Word)
            .join(UserWord)
            .filter(UserWord.user_id == user_id, ~Word.is_common)
            .all()
        )

        return words
