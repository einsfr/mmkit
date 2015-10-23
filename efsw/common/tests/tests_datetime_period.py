import datetime

from django.test import TestCase

from efsw.common.datetime import period


class PeriodTestCase(TestCase):

    def test_get_periods(self):
        self.assertEqual(
            period.DatePeriod.get_periods(period.DatePeriod.PERIOD_TODAY),
            {
                period.DatePeriod.PERIOD_TODAY: 'сегодня',
            }
        )
        self.assertEqual(
            period.DatePeriod.get_periods(),
            {
                period.DatePeriod.PERIOD_TODAY: 'сегодня',
                period.DatePeriod.PERIOD_YESTERDAY: 'вчера',
                period.DatePeriod.PERIOD_TOMORROW: 'завтра',
                period.DatePeriod.PERIOD_THIS_WEEK: 'на этой неделе',
                period.DatePeriod.PERIOD_LAST_WEEK: 'на прошлой неделе',
                period.DatePeriod.PERIOD_NEXT_WEEK: 'на следующей неделе',
                period.DatePeriod.PERIOD_THIS_MONTH: 'в этом месяце',
                period.DatePeriod.PERIOD_LAST_MONTH: 'в прошлом месяце',
                period.DatePeriod.PERIOD_NEXT_MONTH: 'в следующем месяце',
                period.DatePeriod.PERIOD_THIS_YEAR: 'в этом году',
                period.DatePeriod.PERIOD_LAST_YEAR: 'в прошлом году',
                period.DatePeriod.PERIOD_NEXT_YEAR: 'в следующем году',
            }
        )
        self.assertEqual(
            period.DatePeriod.get_periods([]),
            period.DatePeriod.get_periods()
        )
        self.assertEqual(
            period.DatePeriod.get_periods([
                period.DatePeriod.PERIOD_YESTERDAY,
                period.DatePeriod.PERIOD_THIS_MONTH,
                period.DatePeriod.PERIOD_LAST_YEAR,
            ]),
            {
                period.DatePeriod.PERIOD_YESTERDAY: 'вчера',
                period.DatePeriod.PERIOD_THIS_MONTH: 'в этом месяце',
                period.DatePeriod.PERIOD_LAST_YEAR: 'в прошлом году',
            }
        )
        self.assertEqual(
            period.DatePeriod.get_periods([
                period.DatePeriod.PERIOD_LAST_YEAR,
                period.DatePeriod.PERIOD_NEXT_WEEK,
                period.DatePeriod.PERIOD_NEXT_YEAR,
            ]),
            {
                period.DatePeriod.PERIOD_LAST_YEAR: 'в прошлом году',
                period.DatePeriod.PERIOD_NEXT_WEEK: 'на следующей неделе',
                period.DatePeriod.PERIOD_NEXT_YEAR: 'в следующем году',
            }
        )
        self.assertEqual(
            period.DatePeriod.get_periods([
                period.DatePeriod.PERIOD_TOMORROW,
                9999999,
                period.DatePeriod.PERIOD_NEXT_YEAR,
            ]),
            {
                period.DatePeriod.PERIOD_TOMORROW: 'завтра',
                period.DatePeriod.PERIOD_NEXT_YEAR: 'в следующем году',
            }
        )
        with self.assertRaises(period.PeriodDoesNotExist):
            period.DatePeriod.get_periods([
                period.DatePeriod.PERIOD_TOMORROW,
                9999999,
                period.DatePeriod.PERIOD_NEXT_YEAR,
            ], True)
        try:
            period.DatePeriod.get_periods([
                period.DatePeriod.PERIOD_TOMORROW,
                9999999,
                period.DatePeriod.PERIOD_NEXT_YEAR,
            ], True)
        except period.PeriodDoesNotExist as exc:
            self.assertEqual(
                exc.periods,
                [9999999]
            )
        self.assertEqual(
            period.DatePeriod.get_periods([
                period.DatePeriod.PERIOD_LAST_YEAR,
                period.DatePeriod.PERIOD_NEXT_WEEK,
                period.DatePeriod.PERIOD_NEXT_YEAR,
            ], True),
            {
                period.DatePeriod.PERIOD_LAST_YEAR: 'в прошлом году',
                period.DatePeriod.PERIOD_NEXT_WEEK: 'на следующей неделе',
                period.DatePeriod.PERIOD_NEXT_YEAR: 'в следующем году',
            }
        )
        past_dict = {
            period.DatePeriod.PERIOD_TODAY: 'сегодня',
            period.DatePeriod.PERIOD_YESTERDAY: 'вчера',
            period.DatePeriod.PERIOD_THIS_WEEK: 'на этой неделе',
            period.DatePeriod.PERIOD_LAST_WEEK: 'на прошлой неделе',
            period.DatePeriod.PERIOD_THIS_MONTH: 'в этом месяце',
            period.DatePeriod.PERIOD_LAST_MONTH: 'в прошлом месяце',
            period.DatePeriod.PERIOD_THIS_YEAR: 'в этом году',
            period.DatePeriod.PERIOD_LAST_YEAR: 'в прошлом году',
        }
        self.assertEqual(
            period.DatePeriod.get_periods_past_only(),
            past_dict
        )
        del past_dict[period.DatePeriod.PERIOD_TODAY]
        self.assertEqual(
            period.DatePeriod.get_periods_past_only(False),
            past_dict
        )
        future_dict = {
            period.DatePeriod.PERIOD_TODAY: 'сегодня',
            period.DatePeriod.PERIOD_TOMORROW: 'завтра',
            period.DatePeriod.PERIOD_THIS_WEEK: 'на этой неделе',
            period.DatePeriod.PERIOD_NEXT_WEEK: 'на следующей неделе',
            period.DatePeriod.PERIOD_THIS_MONTH: 'в этом месяце',
            period.DatePeriod.PERIOD_NEXT_MONTH: 'в следующем месяце',
            period.DatePeriod.PERIOD_THIS_YEAR: 'в этом году',
            period.DatePeriod.PERIOD_NEXT_YEAR: 'в следующем году',
        }
        self.assertEqual(
            period.DatePeriod.get_periods_future_only(),
            future_dict
        )
        del future_dict[period.DatePeriod.PERIOD_TODAY]
        self.assertEqual(
            period.DatePeriod.get_periods_future_only(False),
            future_dict
        )

    def test_get(self):
        self.assertIsNone(period.DatePeriod.get(9999999))
        with self.assertRaises(period.PeriodDoesNotExist):
            period.DatePeriod.get(9999999, strict=True)
        try:
            period.DatePeriod.get(9999999, strict=True)
        except period.PeriodDoesNotExist as exc:
            self.assertEqual(
                exc.periods,
                9999999
            )
        with self.assertRaises(TypeError):
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_TODAY,
                'some-string'
            )
        self.assertEqual(
            period.DatePeriod.get(period.DatePeriod.PERIOD_TODAY),
            (
                datetime.date.today(),
                datetime.date.today(),
            )
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_TODAY,
                date=datetime.date.today()
            ),
            (
                datetime.date.today(),
                datetime.date.today(),
            )
        )
        test_date = datetime.date(2015, 2, 22)
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_TODAY,
                date=test_date
            ),
            (test_date, test_date)
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_YESTERDAY,
                date=test_date
            ),
            (datetime.date(2015, 2, 21), datetime.date(2015, 2, 21))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_TOMORROW,
                date=test_date
            ),
            (datetime.date(2015, 2, 23), datetime.date(2015, 2, 23))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_WEEK,
                date=test_date
            ),
            (datetime.date(2015, 2, 16), datetime.date(2015, 2, 22))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_WEEK,
                date=test_date,
                mode=period.DatePeriod.MODE_PAST_ONLY
            ),
            (datetime.date(2015, 2, 16), datetime.date(2015, 2, 21))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_WEEK,
                date=test_date,
                mode=period.DatePeriod.MODE_PAST_ONLY_WITH_TODAY
            ),
            (datetime.date(2015, 2, 16), datetime.date(2015, 2, 22))
        )
        self.assertIsNone(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_WEEK,
                date=test_date,
                mode=period.DatePeriod.MODE_FUTURE_ONLY
            )
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_WEEK,
                date=test_date,
                mode=period.DatePeriod.MODE_FUTURE_ONLY_WITH_TODAY
            ),
            (datetime.date(2015, 2, 22), datetime.date(2015, 2, 22))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_LAST_WEEK,
                date=test_date
            ),
            (datetime.date(2015, 2, 9), datetime.date(2015, 2, 15))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_NEXT_WEEK,
                date=test_date
            ),
            (datetime.date(2015, 2, 23), datetime.date(2015, 3, 1))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_MONTH,
                date=test_date
            ),
            (datetime.date(2015, 2, 1), datetime.date(2015, 2, 28))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_MONTH,
                date=test_date,
                mode=period.DatePeriod.MODE_PAST_ONLY
            ),
            (datetime.date(2015, 2, 1), datetime.date(2015, 2, 21))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_MONTH,
                date=test_date,
                mode=period.DatePeriod.MODE_PAST_ONLY_WITH_TODAY
            ),
            (datetime.date(2015, 2, 1), datetime.date(2015, 2, 22))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_MONTH,
                date=test_date,
                mode=period.DatePeriod.MODE_FUTURE_ONLY
            ),
            (datetime.date(2015, 2, 23), datetime.date(2015, 2, 28))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_MONTH,
                date=test_date,
                mode=period.DatePeriod.MODE_FUTURE_ONLY_WITH_TODAY
            ),
            (datetime.date(2015, 2, 22), datetime.date(2015, 2, 28))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_LAST_MONTH,
                date=test_date
            ),
            (datetime.date(2015, 1, 1), datetime.date(2015, 1, 31))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_NEXT_MONTH,
                date=test_date
            ),
            (datetime.date(2015, 3, 1), datetime.date(2015, 3, 31))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_YEAR,
                date=test_date
            ),
            (datetime.date(2015, 1, 1), datetime.date(2015, 12, 31))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_YEAR,
                date=test_date,
                mode=period.DatePeriod.MODE_PAST_ONLY
            ),
            (datetime.date(2015, 1, 1), datetime.date(2015, 2, 21))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_YEAR,
                date=test_date,
                mode=period.DatePeriod.MODE_PAST_ONLY_WITH_TODAY
            ),
            (datetime.date(2015, 1, 1), datetime.date(2015, 2, 22))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_YEAR,
                date=test_date,
                mode=period.DatePeriod.MODE_FUTURE_ONLY
            ),
            (datetime.date(2015, 2, 23), datetime.date(2015, 12, 31))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_THIS_YEAR,
                date=test_date,
                mode=period.DatePeriod.MODE_FUTURE_ONLY_WITH_TODAY
            ),
            (datetime.date(2015, 2, 22), datetime.date(2015, 12, 31))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_LAST_YEAR,
                date=test_date
            ),
            (datetime.date(2014, 1, 1), datetime.date(2014, 12, 31))
        )
        self.assertEqual(
            period.DatePeriod.get(
                period.DatePeriod.PERIOD_NEXT_YEAR,
                date=test_date
            ),
            (datetime.date(2016, 1, 1), datetime.date(2016, 12, 31))
        )