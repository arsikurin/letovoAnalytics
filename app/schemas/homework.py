from typing import Optional

from pydantic import BaseModel, Field


class HomeworkAttendance(BaseModel):
    # id_attendance: int
    # attendance_period: int
    # attendance_student: int
    # attendance_subject: int
    # attendance_group: int
    # attendance_lesson: int
    # attendance_date: str
    attendance_reason: Optional[str]


class HomeworkSubject(BaseModel):
    # id_subject: int
    subject_name: str
    subject_name_eng: Optional[str]
    # subject_order: int
    # subject_group: str
    # subject_development: int


class HomeworkGroup(BaseModel):
    # id_group: int
    group_name: str
    # group_hour: int
    # group_hour_week: int
    # group_level: str
    # group_subject: int
    subject: HomeworkSubject
    # group_teachers: Optional[list]


class HomeworkRoom(BaseModel):
    # id_room: int
    room_name: str
    room_description: str


class HomeworkWorkList(BaseModel):
    # id_work: int
    work_comment: Optional[str]
    # work_lesson: int
    work_criterion: Optional[str]
    work_form: int
    # work_obligatory: int
    # form: Optional[dict]
    # mark_list: list


class HomeworkLessonsList(BaseModel):
    # id_lesson: int
    # lesson_period: int
    # lesson_group: str
    # lesson_date: str
    # lesson_num: int
    lesson_topic: Optional[str] = Field(alias="lesson_thema")
    lesson_canvas: int
    lesson_url: Optional[str]
    lesson_hw: Optional[str]
    lesson_hw_date: Optional[str]
    lesson_hw_url: Optional[str]
    # lesson_hw_duration: int
    lesson_comment: Optional[str]
    # lesson_de: int
    # work: list[HomeworkWorkList]
    attendance: list[HomeworkAttendance]


class HomeworkZoomMeetings(BaseModel):
    # meeting_id: int
    # meeting_topic: str
    # meeting_group_id: int
    # meeting_shedule_day: int
    # meeting_shedule_lesson: str
    meeting_url: str


class HomeworkList(BaseModel):
    # id_schedule: int = Field(alias="id_shedule")
    # schedule_period: int = Field(alias="shedule_period")
    # schedule_group: int = Field(alias="shedule_group")
    # schedule_room: int = Field(alias="shedule_room")
    lessons: list[HomeworkLessonsList]
    zoom_meetings: Optional[HomeworkZoomMeetings]
    # program_dev_type: str
    group: HomeworkGroup
    room: HomeworkRoom


class HomeworkDataList(BaseModel):
    # id_period: int
    # period_year: int
    period_num_day: int
    period_name: str
    # period_num: int
    # period_shortname: str
    period_start: str
    period_end: str
    # period_order: str
    # period_feed: int
    # period_feed_name: Optional[str]
    date: str
    schedules: list[HomeworkList]


class HomeworkResponse(BaseModel):
    status: str
    code: int
    detail: str = Field(alias="message")
    data: list[HomeworkDataList]
