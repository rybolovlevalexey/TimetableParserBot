from pydantic import BaseModel, Field
from typing import Optional


class LessonModel(BaseModel):
    name_lesson: str
    time: str
    teacher: Optional[str]
    cabinet: Optional[str]
    more_info: Optional[dict[str, bool]]


class WeekScheduleExtraInfo(BaseModel):
    cancelled_lessons: bool = Field(default=False, description="Есть ли на неделе отменённые занятия")
