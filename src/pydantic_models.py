from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# МОДЕЛИ ДЛЯ ПАРСИНГА
# результат сбора информации о расписании, модель для описания конкретного занятия
class LessonModel(BaseModel):
    name_lesson: str
    time: str
    teacher: Optional[str]
    cabinet: Optional[str]
    more_info: Optional[dict[str, bool]]


# модель для выведения дополнительной информации о недельном расписании после парсинга
class WeekScheduleExtraInfo(BaseModel):
    cancelled_lessons: bool = Field(default=False, description="Есть ли на неделе отменённые занятия")


# МОДЕЛИ ДЛЯ API
# модель пользователя
class User(BaseModel):
    login: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


# модель пользователя с хэшированным паролем
class UserInDB(User):
    hashed_password: str


# Модель для ответа с токеном
class Token(BaseModel):
    access_token: str
    token_type: str


# Модель для запроса с токеном
class TokenInput(BaseModel):
    access_token: str
