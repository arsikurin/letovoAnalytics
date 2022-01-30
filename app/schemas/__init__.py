from .marks import MarksResponse, DataList as MarksDataList
from .schedule import ScheduleResponse, ScheduleResponse as HomeworkResponse
# from .homework import HomeworkResponse
from .teachers import TeachersResponse

__all__ = (
    "MarksResponse",
    "MarksDataList",
    "ScheduleResponse",
    "HomeworkResponse",
    "TeachersResponse"
)
