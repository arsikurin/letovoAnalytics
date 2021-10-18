#!/usr/bin/python3.10

from pydantic import BaseModel, Field
from typing import Optional


#
# I commented out useless fields
#


class MarksList(BaseModel):
    # id_mark: int
    # mark_period: int
    # mark_student: int
    # mark_group: int
    # mark_work: int
    mark_value: str
    mark_criterion: Optional[str]
    # created_at: str
    # deleted_at: Optional[str]
    # id_lesson: int
    # lesson_date: str
    # lesson_num: int
    # lesson_thema: Optional[str]
    # work_comment: Optional[str]
    form_name: Optional[str]
    form_description: Optional[str]
    # form_description_eng: Optional[str]
    # comment_list: list


class MarksSubject(BaseModel):
    # id_subject: int
    subject_name: str
    subject_name_eng: Optional[str]
    # subject_order: int
    # subject_group: str
    # subject_development: int


class MarksGroup(BaseModel):
    # id_group: int
    group_name: str
    # group_subject: str
    group_level: str
    # group_hour: int
    # group_hour_week: int
    subject: MarksSubject


class MarksDataList(BaseModel):
    # id_group: int
    formative_avg_value: Optional[int]
    summative_avg_value: Optional[int]
    # criterions_summative_mark_list: list
    formative_list: list[Optional[MarksList]]
    # formative_dynamic_status: str
    summative_list: list[Optional[MarksList]]
    # summative_dynamic_status: str
    group_avg_mark: Optional[str]
    # target_mark: Optional[int]
    # final_mark_list: list
    # result_final_mark: Union[None, str, int]
    group: MarksGroup


class MarksResponse(BaseModel):
    # status: str
    # code: int
    # message: str
    data: list[MarksDataList]


class ScheduleAttendance(BaseModel):
    # id_attendance: int
    # attendance_period: int
    # attendance_student: int
    # attendance_subject: int
    # attendance_group: int
    # attendance_lesson: int
    # attendance_date: str
    attendance_reason: Optional[str]


class ScheduleSubject(BaseModel):
    # id_subject: int
    subject_name: str
    subject_name_eng: str
    # subject_order: int
    # subject_group: str
    # subject_development: int


class ScheduleGroup(BaseModel):
    # id_group: int
    group_name: str
    # group_hour: int
    # group_hour_week: int
    # group_level: str
    # group_subject: int
    subject: ScheduleSubject
    # group_teachers: Optional[list]


class ScheduleRoom(BaseModel):
    # id_room: int
    room_name: str
    room_description: str


class ScheduleWorkList(BaseModel):
    # id_work: int
    work_comment: Optional[str]
    # work_lesson: int
    work_criterion: Optional[str]
    work_form: int
    # work_obligatory: int
    # form: Optional[dict]
    # mark_list: list


class ScheduleLessonsList(BaseModel):
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
    # work: list[ScheduleWorkList]
    attendance: list[ScheduleAttendance]


class ScheduleList(BaseModel):
    # id_schedule: int = Field(alias="id_shedule")
    # schedule_period: int = Field(alias="shedule_period")
    # schedule_group: int = Field(alias="shedule_group")
    schedule_room: int = Field(alias="shedule_room")
    lessons: list[ScheduleLessonsList]
    zoom_meetings: Optional[list]
    # program_dev_type: str
    group: ScheduleGroup
    room: ScheduleRoom


class ScheduleDataList(BaseModel):
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
    schedules: list[ScheduleList]


class ScheduleResponse(BaseModel):
    # status: str
    # code: int
    # message: str
    data: list[ScheduleDataList]
