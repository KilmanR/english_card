import streamlit as st
import random
from sqlalchemy.exc import SQLAlchemyError
from models import init_db
from db import (
    get_or_create_user,
    get_user_words,
    add_word,
    delete_word,
    update_word_stats,
    get_user_stats,
    get_user_personal_words,
)

st.set_page_config(page_title="EnglishCard", page_icon="📚")

if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

if "user" not in st.session_state:
    st.session_state.user = None
if "current_word" not in st.session_state:
    st.session_state.current_word = None
if "options" not in st.session_state:
    st.session_state.options = []
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "is_correct" not in st.session_state:
    st.session_state.is_correct = False


def main():
    st.title("📚 EnglishCard")
    st.markdown("### Приложение для изучения английского языка")

    if st.session_state.user is None:
        show_welcome()
    else:
        show_menu()


def show_welcome():
    st.markdown("### Добро пожаловать!")
    st.markdown("Введите ваше имя для начала:")

    username = st.text_input("Ваше имя:", key="username_input")

    if st.button("Начать изучение"):
        username = username.strip()
        if not username:
            st.warning("Пожалуйста, введите имя!")
        elif len(username) > 100:
            st.error("Имя не должно превышать 100 символов!")
        else:
            try:
                st.session_state.user = get_or_create_user(username)
                st.rerun()
            except SQLAlchemyError:
                st.error("Ошибка при создании пользователя. Попробуйте ещё раз.")


def show_menu():
    with st.sidebar:
        st.write(f"👤 Пользователь: **{st.session_state.user.username}**")
        st.divider()

        menu = st.radio(
            "Меню",
            [
                "🎯 Тренировка",
                "➕ Добавить слово",
                "🗑️ Удалить слово",
                "📊 Статистика",
                "🚪 Выйти",
            ],
        )

        if menu == "🚪 Выйти":
            st.session_state.user = None
            st.rerun()

    if menu == "🎯 Тренировка":
        training_page()
    elif menu == "➕ Добавить слово":
        add_word_page()
    elif menu == "🗑️ Удалить слово":
        delete_word_page()
    elif menu == "📊 Статистика":
        stats_page()


def training_page():
    st.header("🎯 Тренировка слов")

    try:
        words = get_user_words(st.session_state.user.id)
    except SQLAlchemyError:
        st.error("Ошибка при загрузке слов.")
        return

    if not words:
        st.warning("У вас пока нет слов для тренировки. Добавьте слова!")
        return

    if st.session_state.current_word is None:
        st.session_state.current_word = random.choice(words)
        st.session_state.show_result = False

        all_words = get_user_words(st.session_state.user.id)
        other_words = [
            w for w in all_words if w.id != st.session_state.current_word.id
        ]
        wrong_options = random.sample(other_words, min(3, len(other_words)))

        options = [st.session_state.current_word] + wrong_options
        random.shuffle(options)
        st.session_state.options = options

    current = st.session_state.current_word
    st.markdown(f"### Переведите слово: **{current.word_ru}**")

    if not st.session_state.show_result:
        cols = st.columns(2)
        for i, option in enumerate(st.session_state.options):
            with cols[i % 2]:
                if st.button(option.word_en, key=f"option_{option.id}"):
                    is_correct = option.id == current.id
                    st.session_state.show_result = True
                    st.session_state.is_correct = is_correct

                    try:
                        update_word_stats(
                            st.session_state.user.id, current.id, is_correct
                        )
                    except SQLAlchemyError:
                        st.error("Ошибка при сохранении результата.")

                    st.rerun()
    else:
        if st.session_state.is_correct:
            st.success("✅ Правильно! Молодец!")
        else:
            st.error(f"❌ Неверно. Правильный ответ: **{current.word_en}**")

        st.divider()
        if st.button("➡️ Следующее слово", type="primary"):
            st.session_state.current_word = None
            st.session_state.show_result = False
            st.rerun()


def add_word_page():
    st.header("➕ Добавить новое слово")

    col1, col2 = st.columns(2)
    with col1:
        word_en = st.text_input("Слово на английском:", key="add_en")
    with col2:
        word_ru = st.text_input("Перевод на русский:", key="add_ru")

    if st.button("Добавить слово"):
        word_en = word_en.strip()
        word_ru = word_ru.strip()
        if word_en and word_ru:
            try:
                add_word(word_en, word_ru, st.session_state.user.id)
                st.success(f"✅ Слово '{word_en}' добавлено!")
                st.balloons()
            except SQLAlchemyError:
                st.error("Ошибка при добавлении слова.")
        else:
            st.warning("Заполните оба поля!")


def delete_word_page():
    st.header("🗑️ Удалить слово")

    try:
        user_words = get_user_personal_words(st.session_state.user.id)
    except SQLAlchemyError:
        st.error("Ошибка при загрузке слов.")
        return

    if not user_words:
        st.info("У вас нет личных слов для удаления.")
        return

    word_options = {f"{word.word_en} - {word.word_ru}": word.id for word in user_words}

    selected = st.selectbox("Выберите слово для удаления:", list(word_options.keys()))

    if st.button("Удалить"):
        word_id = word_options[selected]
        if delete_word(word_id, st.session_state.user.id):
            st.success("✅ Слово удалено!")
            st.rerun()
        else:
            st.error("Не удалось удалить слово. Оно может быть общим или уже удалено.")


def stats_page():
    st.header("📊 Ваша статистика")

    try:
        stats = get_user_stats(st.session_state.user.id)
    except SQLAlchemyError:
        st.error("Ошибка при загрузке статистики.")
        return

    if stats["total_words"]:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Всего слов", stats["total_words"])

        with col2:
            st.metric("Правильных ответов", stats["total_correct"])

        with col3:
            accuracy = 0.0
            if stats["total_attempts"] > 0:
                accuracy = round(
                    (stats["total_correct"] / stats["total_attempts"]) * 100, 1
                )
            st.metric("Точность", f"{accuracy}%")

        st.divider()
        st.write(f"🎯 Выучено слов: **{stats['learned_words']}**")
    else:
        st.info("Пока нет статистики. Начните тренировку!")


if __name__ == "__main__":
    main()
