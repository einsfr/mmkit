import datetime
import calendar


class PeriodDoesNotExist(Exception):
    def __init__(self, periods):
        self.periods = periods
        msg = 'Следующие идентификаторы периодов не определены: {0}'.format(periods)
        super().__init__(msg)


class DatePeriod():

    PERIOD_TODAY = 1
    PERIOD_YESTERDAY = 2
    PERIOD_TOMORROW = 3
    PERIOD_THIS_WEEK = 4
    PERIOD_LAST_WEEK = 5
    PERIOD_NEXT_WEEK = 6
    PERIOD_THIS_MONTH = 7
    PERIOD_LAST_MONTH = 8
    PERIOD_NEXT_MONTH = 9
    PERIOD_THIS_YEAR = 10
    PERIOD_LAST_YEAR = 11
    PERIOD_NEXT_YEAR = 12

    MODE_PAST_ONLY = 1
    MODE_PAST_ONLY_WITH_TODAY = 2
    MODE_FUTURE_ONLY = 3
    MODE_FUTURE_ONLY_WITH_TODAY = 4

    PERIODS_PAST_ONLY = [
        PERIOD_YESTERDAY,
        PERIOD_THIS_WEEK,
        PERIOD_LAST_WEEK,
        PERIOD_THIS_MONTH,
        PERIOD_LAST_MONTH,
        PERIOD_THIS_YEAR,
        PERIOD_LAST_YEAR
    ]

    PERIODS_PAST_ONLY_WITH_TODAY = [PERIOD_TODAY] + PERIODS_PAST_ONLY

    PERIODS_FUTURE_ONLY = [
        PERIOD_TOMORROW,
        PERIOD_THIS_WEEK,
        PERIOD_NEXT_WEEK,
        PERIOD_THIS_MONTH,
        PERIOD_NEXT_MONTH,
        PERIOD_THIS_YEAR,
        PERIOD_NEXT_YEAR
    ]

    PERIODS_FUTURE_ONLY_WITH_TODAY = [PERIOD_TODAY] + PERIODS_FUTURE_ONLY

    @classmethod
    def _get_period_titles(cls):
        return {
            cls.PERIOD_TODAY: 'сегодня',
            cls.PERIOD_YESTERDAY: 'вчера',
            cls.PERIOD_TOMORROW: 'завтра',
            cls.PERIOD_THIS_WEEK: 'на этой неделе',
            cls.PERIOD_LAST_WEEK: 'на прошлой неделе',
            cls.PERIOD_NEXT_WEEK: 'на следующей неделе',
            cls.PERIOD_THIS_MONTH: 'в этом месяце',
            cls.PERIOD_LAST_MONTH: 'в прошлом месяце',
            cls.PERIOD_NEXT_MONTH: 'в следующем месяце',
            cls.PERIOD_THIS_YEAR: 'в этом году',
            cls.PERIOD_LAST_YEAR: 'в прошлом году',
            cls.PERIOD_NEXT_YEAR: 'в следующем году',
        }

    @classmethod
    def get_periods(cls, periods=[], strict=False):
        period_titles = cls._get_period_titles()
        if type(periods) != list:
            periods = [periods]
        if len(periods) == 0:
            return period_titles
        result = dict((k, v) for k, v in period_titles.items() if k in periods)
        if strict and (len(periods) != len(result)):
            raise PeriodDoesNotExist([x for x in periods if period_titles.get(x) is None])
        return result

    @classmethod
    def get_periods_past_only(cls, include_today=True):
        if include_today:
            return cls.get_periods(cls.PERIODS_PAST_ONLY_WITH_TODAY)
        else:
            return cls.get_periods(cls.PERIODS_PAST_ONLY)

    @classmethod
    def get_periods_future_only(cls, include_today=True):
        if include_today:
            return cls.get_periods(cls.PERIODS_FUTURE_ONLY_WITH_TODAY)
        else:
            return cls.get_periods(cls.PERIODS_FUTURE_ONLY)

    @classmethod
    def get(cls, period, date=None, strict=False, mode=0):
        if date is None:
            date = datetime.date.today()
        elif not isinstance(date, datetime.date):
            msg = 'Метод DatePeriod.get() принимает в качестве аргумента date только экземпляр класса datetime.date'
            raise TypeError(msg)
        start = None
        end = None
        if mode == cls.MODE_PAST_ONLY:
            end = date - datetime.timedelta(1)
        elif mode == cls.MODE_PAST_ONLY_WITH_TODAY:
            end = date
        elif mode == cls.MODE_FUTURE_ONLY:
            start = date + datetime.timedelta(1)
        elif mode == cls.MODE_FUTURE_ONLY_WITH_TODAY:
            start = date
        if period == cls.PERIOD_TODAY:
            return date, date
        elif period == cls.PERIOD_YESTERDAY:
            start = end = date - datetime.timedelta(1)
            return start, end
        elif period == cls.PERIOD_TOMORROW:
            start = end = date + datetime.timedelta(1)
            return start, end
        elif period == cls.PERIOD_THIS_WEEK:
            if start is None:
                start = date - datetime.timedelta(date.weekday())
            if end is None:
                end = date + datetime.timedelta(6 - date.weekday())
            if start > end:
                return None
            else:
                return start, end
        elif period == cls.PERIOD_LAST_WEEK:
            start = date - datetime.timedelta(7 + date.weekday())
            end = date - datetime.timedelta(13 - date.weekday())
            return start, end
        elif period == cls.PERIOD_NEXT_WEEK:
            start = date + datetime.timedelta(7 - date.weekday())
            end = date + datetime.timedelta(13 - date.weekday())
            return start, end
        elif period == cls.PERIOD_THIS_MONTH:
            if start is None:
                start = date.replace(day=1)
            if end is None:
                end = date.replace(day=calendar.monthrange(date.year, date.month)[1])
            if start > end:
                return None
            else:
                return start, end
        elif period == cls.PERIOD_LAST_MONTH:
            last_day_of_previous_month = date.replace(day=1) - datetime.timedelta(1)
            start = last_day_of_previous_month.replace(day=1)
            return start, last_day_of_previous_month
        elif period == cls.PERIOD_NEXT_MONTH:
            last_day_of_this_month = date.replace(
                day=calendar.monthrange(date.year, date.month)[1]
            )
            start = last_day_of_this_month + datetime.timedelta(1)
            end = start.replace(day=calendar.monthrange(start.year, start.month)[1])
            return start, end
        elif period == cls.PERIOD_THIS_YEAR:
            if start is None:
                start = date.replace(month=1, day=1)
            if end is None:
                end = date.replace(month=12, day=31)
            if start > end:
                return None
            else:
                return start, end
        elif period == cls.PERIOD_LAST_YEAR:
            prev_year = date.year - 1
            start = date.replace(year=prev_year, month=1, day=1)
            end = date.replace(year=prev_year, month=12, day=31)
            return start, end
        elif period == cls.PERIOD_NEXT_YEAR:
            next_year = date.year + 1
            start = date.replace(year=next_year, month=1, day=1)
            end = date.replace(year=next_year, month=12, day=31)
            return start, end
        else:
            if strict:
                raise PeriodDoesNotExist(period)
            else:
                return None