from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.ext.hybrid import hybrid_property

from src.config import settings

DB_URL: str = settings.get_db_url()

engine = create_async_engine(DB_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


# Основная таблица базы данных пользователей с общей информацией и необходимым минимумом для авторизации
class User(Base):
    __tablename__ = "users"

    login: Mapped[str]
    full_name: Mapped[str] = mapped_column(String, default="")
    email: Mapped[str] = mapped_column(String)
    disabled: Mapped[bool] = mapped_column(Boolean)
    hashed_password: Mapped[str] = mapped_column(String)


# Таблица с информацией о факультетах
class Faculty(Base):
    __tablename__ = "faculties"

    name: Mapped[str] = mapped_column(String, unique=True)
    url: Mapped[str] = mapped_column(String, unique=True)
    # связь с моделью EduProgram - список образовательных программ этого факультета
    edu_programs = relationship("EduProgram", back_populates="faculty")


# Таблица с информацией о направлениях
class EduProgram(Base):
    __tablename__ = "edu_programs"

    name: Mapped[str] = mapped_column(String)
    year: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String, unique=True)
    # связь с моделью Faculty - имя факультета / модель факультета целиком (на котором находится данная программа)
    faculty_name: Mapped[str] = mapped_column(String, ForeignKey("faculties.name"))
    faculty = relationship("Faculty", back_populates="edu_programs")
    # связь с моделью StudyGroup - список всех групп данной образовательной программы
    groups = relationship("StudyGroup", back_populates="edu_program")

    # создание полного названия образовательной программы = название + год поступления
    @hybrid_property
    def program_full_name(self) -> str:
        return f"{self.name} {self.year}"


# Таблица с информацией об образовательных группах
class StudyGroup(Base):
    __tablename__ = "studying_groups"

    name: Mapped[str]
    url: Mapped[str] = mapped_column(String, unique=True)
    # связь с моделью EduProgram - название программы / модель программы целиком (к которой принадлежит данная группа)
    edu_program_id: Mapped[int] = mapped_column(Integer, ForeignKey("edu_programs.id"))
    edu_program = relationship("EduProgram", back_populates="groups")
