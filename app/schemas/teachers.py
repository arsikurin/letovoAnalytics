from typing import Optional

from pydantic import BaseModel


class Subject(BaseModel):
    # id_subject: int
    subject_name: str
    subject_name_eng: Optional[str]
    # subject_order: int
    # subject_group: str
    # subject_development: int


class Teacher(BaseModel):
    # id_teacher: int
    teacher_surname: str
    teacher_name: str
    teacher_fath: str
    # teacher_surname_eng: str
    # teacher_name_eng: str
    # teacher_fath_eng: Optional[str]
    teacher_mail: str


class GroupTeachers(BaseModel):
    # id_group: int
    # id_teacher: int
    teacher: Teacher


class Group(BaseModel):
    # id_group: int
    group_name: str
    # group_subject: str
    # group_level: str
    # group_hour: int
    # group_hour_week: int
    subject: Subject
    group_teachers: list[GroupTeachers]


class DataList(BaseModel):
    # id_group: int
    # formative_avg_value: Optional[int]
    # summative_avg_value: Optional[int]
    # criterions_summative_mark_list: list
    # formative_list: list[MarksList]
    # formative_dynamic_status: str
    # summative_list: list[MarksList]
    # summative_dynamic_status: str
    # group_avg_mark: Optional[str]
    # target_mark: Optional[int]
    # final_mark_list: list[FinalMarkList]
    # result_final_mark: Optional[str]
    group: Group


class TeachersResponse(BaseModel):
    # status: str
    # code: int
    # message: str
    data: list[DataList]
