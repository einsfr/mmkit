from django.db import models


class Lineup(models.Model):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'сетка вещания'
        verbose_name_plural = 'сетки вещания'

    name = models.CharField(
        max_length=255,
        verbose_name='название',
        unique=True
    )

    active_since = models.DateField(
        verbose_name='используется с'
    )

    active_until = models.DateField(
        verbose_name='используется до'
    )

    active = models.BooleanField(
        verbose_name='используется'
    )

    def __str__(self):
        return self.name


class Program(models.Model):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'программа'
        verbose_name_plural = 'программы'

    AGE_LIMIT_0 = 0
    AGE_LIMIT_6 = 6
    AGE_LIMIT_12 = 12
    AGE_LIMIT_16 = 16
    AGE_LIMIT_18 = 18

    AGE_LIMIT_DICT = {
        AGE_LIMIT_0: '0+',
        AGE_LIMIT_6: '6+',
        AGE_LIMIT_12: '12+',
        AGE_LIMIT_16: '16+',
        AGE_LIMIT_18: '18+',
    }

    name = models.CharField(
        max_length=255,
        verbose_name='название',
        unique=True
    )

    lineup_size = models.TimeField(
        verbose_name='размер в сетке вещания'
    )

    max_duration = models.TimeField(
        verbose_name='максимальный хронометраж'
    )

    min_duration = models.TimeField(
        verbose_name='минимальный хронометраж'
    )

    description = models.TextField(
        verbose_name='описание'
    )

    age_limit = models.SmallIntegerField(
        choices=AGE_LIMIT_DICT.items(),
        verbose_name='ограничение по возрасту'
    )


class ProgramPosition(models.Model):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'положение программы в сетке вещания'
        verbose_name_plural = 'положения программы в сетке вещания'

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    DOW_DICT = {
        MONDAY: 'Понедельник',
        TUESDAY: 'Вторник',
        WEDNESDAY: 'Среда',
        THURSDAY: 'Четверг',
        FRIDAY: 'Пятница',
        SATURDAY: 'Суббота',
        SUNDAY: 'Воскресенье',
    }

    dow = models.SmallIntegerField(
        verbose_name='день недели',
        choices=DOW_DICT.items()
    )

    start_time = models.TimeField(
        verbose_name='время начала'
    )

    comment = models.CharField(
        verbose_name='комментарий',
        max_length=32
    )