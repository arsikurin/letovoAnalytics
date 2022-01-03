from .login import router as login_router
from .schedule import router as schedule_router
from .marks import router as marks_router
from .table import router as table_router

__all__ = ("schedule_router", "login_router", "marks_router")
