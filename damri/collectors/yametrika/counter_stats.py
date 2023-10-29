from damri.collectors.base.collector import BaseDataCollector
from damri.integrations.api.yametrika.api import YaMetrikaCounterStatsAPIClient
from damri.integrations.api.yametrika.filter_params import StatsFilterParam
from damri.integrations.api.yametrika.models import (
    CounterStatModel,
    DeviceCategoryStatModel,
    DeviceStatModel,
    ScreenStatModel,
    SearchStatModel,
    UrlStatModel,
)
from damri.utils.datetime import WordToDateParser


class CounterStatsDataCollector(BaseDataCollector):
    def __init__(self, counter_id: int) -> None:
        super().__init__()
        self.counter_id = counter_id

    def stats_yesterday(self) -> list[CounterStatModel]:
        """
        Конверсия и Достижения, любой цели, за вчерашний день.
        """
        start: str = WordToDateParser(previous_n_day=1, format="%Y-%m-%d")
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=start,
            metrics="ym:s:anyGoalConversionRate,ym:s:sumGoalReachesAny",  # TODO: mv to const ?
            dimensions="ym:s:lastSignDirectClickOrder",
            limit=1000,
            filters="(ym:s:isRobot=='No') and ym:s:LastSignDirectClickOrder!n",
            sort="ym:s:anyGoalConversionRate",
            group="dekaminute",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).counter_stats(params=params)

    def search_stats_bounce(self, start: str, end: str) -> SearchStatModel:
        """
        Статистика по поиску: топ отказы.
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=end,
            metrics="ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
            dimensions="ym:s:lastSearchPhrase",
            limit=1000,
            filters="(ym:s:isRobot=='No') and ym:s:LastSearchPhrase!n",
            sort="-ym:s:bounceRate,-ym:s:users",
            group="day",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).search_stats(params=params)

    def screen_stats_bounce(self, start: str, end: str) -> ScreenStatModel:
        """
        Статистика по экранам: топ отказы.
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=end,
            metrics="ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
            dimensions="ym:s:screenWidth,ym:s:screenHeight",
            limit=1000,
            filters="(ym:s:isRobot=='No') and ym:s:screenWidth!n",
            sort="-ym:s:bounceRate,-ym:s:users",
            group="day",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).screen_stats(params=params)

    def device_stats_bounce(self, start: str, end: str) -> DeviceStatModel:
        """
        Статистика по устройствам: топ отказы.
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=end,
            metrics="ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
            dimensions="ym:s:operatingSystem",
            limit=1000,
            filters="(ym:s:isRobot=='No') and ym:s:screenWidth!n",
            sort="-ym:s:bounceRate,-ym:s:users",
            group="day",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).device_stats(params=params)

    def device_category_stats_bounce(self, start: str, end: str) -> DeviceCategoryStatModel:
        """
        Статистика по тип устройств: топ отказы.
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=end,
            metrics="ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
            dimensions="ym:s:deviceCategory,ym:s:mobilePhone,ym:s:mobilePhoneModel",
            limit=1000,
            filters="(ym:s:isRobot=='No') and ym:s:deviceCategory!n",
            sort="-ym:s:bounceRate,-ym:s:users",
            group="day",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).device_category_stats(params=params)

    def url_stats_bounce(self, start: str, end: str) -> UrlStatModel:
        """
        Статистика по запросам: топ отказы.
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=end,
            metrics="ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
            dimensions=(
                "ym:s:startURLPathLevel1Hash"
                ",ym:s:startURLPathLevel2Hash"
                ",ym:s:startURLPathLevel3Hash"
                ",ym:s:startURLPathLevel4Hash"
                ",ym:s:startURLHash"
            ),
            limit=1000,
            filters="(ym:s:isRobot=='No')",
            sort="-ym:s:bounceRate,-ym:s:users",
            group="day",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).url_stats(params=params)

    def _get_token(self) -> str:
        """
        Процесс получения токена.
        """
        raise NotImplementedError
