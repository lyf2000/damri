from damri.collectors.base.collector import BaseDataCollector
from damri.integrations.api.uis.api import UISJRPCClient
from damri.integrations.api.uis.models import CallReportItemModel, CallSessionItemModel
from damri.utils.datetime import WordToDateParser


class _UISDataCollector(BaseDataCollector):
    def __init__(self) -> None:
        super().__init__()
        self.client = UISJRPCClient()

    def calls_report_prev_week(self) -> list[CallReportItemModel]:
        return self.client.calls_report(*WordToDateParser(last_n_previous_weeks=1))

    def calls_report_prev_month(self) -> list[CallReportItemModel]:
        return self.client.calls_report(*WordToDateParser(last_n_previous_months=1))

    def calls_session_prev_week(self) -> list[CallSessionItemModel]:
        return self.client.calls_session(*WordToDateParser(last_n_previous_weeks=1))


UISDataCollector = _UISDataCollector()
