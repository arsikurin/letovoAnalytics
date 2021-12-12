from typing import Optional

from pydantic import BaseModel


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


class FinalMarkList(BaseModel):
    # if_final: int
    # final_period: int
    # final_student: int
    # final_group: int
    final_value: str
    final_criterion: str
    # final_create: str
    # final_create_user: int
    # final_delete: Optional[str]
    # final_delete_user: Optional[int]


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
    formative_list: list[MarksList]
    # formative_dynamic_status: str
    summative_list: list[MarksList]
    # summative_dynamic_status: str
    group_avg_mark: Optional[str]
    # target_mark: Optional[int]
    final_mark_list: list[FinalMarkList]
    result_final_mark: Optional[str]
    group: MarksGroup


class MarksResponse(BaseModel):
    # status: str
    # code: int
    # message: str
    data: list[MarksDataList]
