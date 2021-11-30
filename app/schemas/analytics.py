from dataclasses import dataclass


@dataclass(slots=True)
class AnalyticsResponse:
    sender_id: str
    message_id: int
    schedule_counter: int
    homework_counter: int
    marks_counter: int
    holidays_counter: int
    clear_counter: int
    options_counter: int
    help_counter: int
    about_counter: int
    inline_counter: int
