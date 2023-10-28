
from damri.models.base import BaseModel
from pydantic import Field


class CallReportItemModel(BaseModel):
    """
    Данные звонка.
    """

    id: int
    is_lost: bool
    finish_reason: str
    contact_phone_number: str
    virtual_phone_number: str


class CallSessionItemModel(BaseModel):
    """
    Данные сессии звонка.
    """

    call_session_id: int
    call_records: list[str] = Field(default_factory=list)
    virtual_phone_number: str
    calling_phone_number: str
    duration: int
    # start_time: datetime
