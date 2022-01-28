from typing import Optional

from pydantic import BaseModel, Field


class TeachersAttendance(BaseModel):
    # id_attendance: int
    # attendance_period: int
    # attendance_student: int
    # attendance_subject: int
    # attendance_group: int
    # attendance_lesson: int
    # attendance_date: str
    attendance_reason: Optional[str]


class TeachersTeacher(BaseModel):
    # id_teacher: int
    teacher_surname: str
    teacher_name: str
    teacher_fath: str
    teacher_surname_eng: str
    # teacher_name_eng: str
    # teacher_fath_eng: Optional[str]
    teacher_mail: str


class TeachersGroupTeachers(BaseModel):
    id_group: int
    id_teacher: int
    teacher: TeachersTeacher


class TeachersSubject(BaseModel):
    # id_subject: int
    subject_name: str
    subject_name_eng: Optional[str]
    # subject_order: int
    # subject_group: str
    # subject_development: int


class TeachersGroup(BaseModel):
    # id_group: int
    group_name: str
    # group_hour: int
    # group_hour_week: int
    # group_level: str
    # group_subject: int
    subject: TeachersSubject
    group_teachers: list[TeachersGroupTeachers]


class TeachersRoom(BaseModel):
    # id_room: int
    room_name: str
    room_description: str


class TeachersWorkList(BaseModel):
    # id_work: int
    work_comment: Optional[str]
    # work_lesson: int
    work_criterion: Optional[str]
    work_form: int
    # work_obligatory: int
    # form: Optional[dict]
    # mark_list: list


class TeachersLessonsList(BaseModel):
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
    # work: list[TeachersWorkList]
    attendance: list[TeachersAttendance]


class TeachersZoomMeetings(BaseModel):
    # meeting_id: int
    # meeting_topic: str
    # meeting_group_id: int
    # meeting_shedule_day: int
    # meeting_shedule_lesson: str
    meeting_url: str


class TeachersList(BaseModel):
    # id_schedule: int = Field(alias="id_shedule")
    # schedule_period: int = Field(alias="shedule_period")
    # schedule_group: int = Field(alias="shedule_group")
    # schedule_room: int = Field(alias="shedule_room")
    # lessons: list[TeachersLessonsList]
    # zoom_meetings: Optional[TeachersZoomMeetings]
    # program_dev_type: str
    group: TeachersGroup
    room: TeachersRoom


class TeachersDataList(BaseModel):
    # id_period: int
    # period_year: int
    # period_num_day: int
    # period_name: str
    # period_num: int
    # period_shortname: str
    # period_start: str
    # period_end: str
    # period_order: str
    # period_feed: int
    # period_feed_name: Optional[str]
    date: str
    schedules: list[TeachersList]


class TeachersResponse(BaseModel):
    # status: str
    # code: int
    # detail: str = Field(alias="message")
    data: list[TeachersDataList]
