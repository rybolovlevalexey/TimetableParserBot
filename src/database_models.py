from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from src.config import settings

DB_URL: str = settings.get_db_url()

engine = create_async_engine(DB_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


# Основная база данных пользователей с общей информацией и необходимым минимумом для авторизации
class User(Base):
    __tablename__ = "users"

    login: Mapped[str]
    full_name: Mapped[str] = mapped_column(String, default="")
    email: Mapped[str] = mapped_column(String)
    disabled: Mapped[bool] = mapped_column(Boolean)
    hashed_password: Mapped[str] = mapped_column(String)
